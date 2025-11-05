"""
Payment API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import Transaction, Contract, User, Client
from app.auth import get_current_user_flexible
from app.api.schemas import PaymentCreate, CryptoPayment, TransactionResponse
from app.payments import (
    create_payment_intent,
    confirm_payment,
    create_payout,
    get_payment_status,
    crypto_handler
)
from app.websocket import manager

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/create", response_model=dict)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Create a payment for a contract (Stripe)

    Args:
        payment_data: Payment creation data
        current_user: Authenticated user
        db: Database session

    Returns:
        Payment intent details
    """
    # Get contract
    contract = db.query(Contract).filter(
        Contract.id == payment_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Verify user is the client
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    if not client or contract.client_id != client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this contract"
        )

    # Create payment intent
    result = await create_payment_intent(
        amount_usd=contract.total_cost_usd,
        contract_id=str(contract.id),
        customer_email=current_user.email
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Payment creation failed")
        )

    # Create transaction record
    transaction = Transaction(
        contract_id=contract.id,
        amount_usd=contract.total_cost_usd,
        payment_method="stripe",
        stripe_payment_id=result["payment_intent_id"],
        status="pending"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Notify via WebSocket
    await manager.notify_payment(
        str(current_user.id),
        str(transaction.id),
        float(contract.total_cost_usd),
        "pending"
    )

    return {
        "transaction_id": str(transaction.id),
        "client_secret": result["client_secret"],
        "payment_intent_id": result["payment_intent_id"],
        "amount": float(contract.total_cost_usd)
    }


@router.post("/crypto", response_model=TransactionResponse)
async def process_crypto_payment(
    payment_data: CryptoPayment,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Process cryptocurrency payment

    Args:
        payment_data: Crypto payment data
        current_user: Authenticated user
        db: Database session

    Returns:
        Transaction details
    """
    # Get contract
    contract = db.query(Contract).filter(
        Contract.id == payment_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Verify user is the client
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    if not client or contract.client_id != client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this contract"
        )

    # Verify payment based on blockchain
    if payment_data.blockchain == "ethereum":
        # Get platform ETH address (would be configured)
        platform_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"  # Example

        result = await crypto_handler.verify_ethereum_payment(
            tx_hash=payment_data.tx_hash,
            expected_amount=contract.total_cost_usd / Decimal('2000'),  # ETH price estimate
            recipient_address=platform_address
        )

    elif payment_data.blockchain == "solana":
        # Get platform SOL address (would be configured)
        platform_address = "SoLPlatformAddress123"  # Example

        result = await crypto_handler.verify_solana_payment(
            tx_signature=payment_data.tx_hash,
            expected_amount=contract.total_cost_usd / Decimal('100'),  # SOL price estimate
            recipient_address=platform_address
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported blockchain"
        )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Payment verification failed")
        )

    # Create transaction record
    transaction = Transaction(
        contract_id=contract.id,
        amount_usd=contract.total_cost_usd,
        payment_method=f"crypto_{payment_data.blockchain}",
        blockchain=payment_data.blockchain,
        tx_hash=payment_data.tx_hash,
        wallet_address=payment_data.wallet_address,
        status="completed" if result.get("verified") else "pending"
    )

    db.add(transaction)

    # Update contract settlement hash
    contract.settlement_hash = payment_data.tx_hash

    db.commit()
    db.refresh(transaction)

    # Notify via WebSocket
    await manager.notify_payment(
        str(current_user.id),
        str(transaction.id),
        float(contract.total_cost_usd),
        transaction.status
    )

    return TransactionResponse.model_validate(transaction)


@router.get("/status/{payment_intent_id}", response_model=dict)
async def check_payment_status(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Check Stripe payment status

    Args:
        payment_intent_id: Stripe payment intent ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Payment status
    """
    result = await get_payment_status(payment_intent_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to get payment status")
        )

    return result


@router.get("/transactions", response_model=list)
async def list_transactions(
    contract_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    List user's transactions

    Args:
        contract_id: Optional filter by contract
        current_user: Authenticated user
        db: Database session

    Returns:
        List of transactions
    """
    query = db.query(Transaction)

    # Filter by user's contracts
    if current_user.role != "admin":
        client = db.query(Client).filter(Client.user_id == current_user.id).first()
        if client:
            user_contracts = db.query(Contract.id).filter(
                Contract.client_id == client.id
            ).all()
            contract_ids = [c.id for c in user_contracts]
            query = query.filter(Transaction.contract_id.in_(contract_ids))

    # Filter by specific contract
    if contract_id:
        query = query.filter(Transaction.contract_id == contract_id)

    transactions = query.order_by(Transaction.created_at.desc()).all()

    return [TransactionResponse.model_validate(t) for t in transactions]


@router.get("/invoice/{client_id}", response_model=dict)
async def generate_invoice(
    client_id: UUID,
    current_user: User = Depends(get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """
    Generate invoice for client

    Args:
        client_id: Client UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        Invoice details
    """
    # Verify access
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    if current_user.role != "admin" and client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this invoice"
        )

    # Get all transactions for client
    transactions = db.query(Transaction).join(Contract).filter(
        Contract.client_id == client_id,
        Transaction.status == "completed"
    ).all()

    total_amount = sum(t.amount_usd for t in transactions)

    return {
        "client_id": str(client_id),
        "org_name": client.org_name,
        "total_transactions": len(transactions),
        "total_amount_usd": float(total_amount),
        "transactions": [
            {
                "id": str(t.id),
                "contract_id": str(t.contract_id),
                "amount": float(t.amount_usd),
                "date": t.created_at.isoformat(),
                "payment_method": t.payment_method
            }
            for t in transactions
        ]
    }
