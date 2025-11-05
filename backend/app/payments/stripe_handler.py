"""
Stripe payment processing
"""

import stripe
from app.config import settings
from typing import Dict, Optional
from decimal import Decimal

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_payment_intent(
    amount_usd: Decimal,
    contract_id: str,
    customer_email: str
) -> Dict:
    """
    Create a Stripe payment intent

    Args:
        amount_usd: Amount in USD
        contract_id: Contract ID for metadata
        customer_email: Customer email

    Returns:
        Payment intent details
    """
    try:
        # Convert to cents
        amount_cents = int(amount_usd * 100)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            metadata={
                "contract_id": contract_id,
                "platform": "mnemo"
            },
            description=f"MNEMO Memory Contract {contract_id}",
            receipt_email=customer_email
        )

        return {
            "success": True,
            "payment_intent_id": intent.id,
            "client_secret": intent.client_secret,
            "status": intent.status
        }

    except stripe.error.CardError as e:
        return {
            "success": False,
            "error": str(e.user_message),
            "error_code": e.code
        }
    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "stripe_error"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "unknown_error"
        }


async def confirm_payment(payment_intent_id: str) -> Dict:
    """
    Confirm a payment intent

    Args:
        payment_intent_id: Stripe payment intent ID

    Returns:
        Confirmation details
    """
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        return {
            "success": True,
            "status": intent.status,
            "amount": intent.amount / 100,  # Convert back to dollars
            "currency": intent.currency
        }

    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": str(e)
        }


async def create_payout(
    amount_usd: Decimal,
    provider_account_id: str,
    node_id: str
) -> Dict:
    """
    Create a payout to provider

    Args:
        amount_usd: Amount to pay out
        provider_account_id: Stripe connected account ID
        node_id: Node ID for metadata

    Returns:
        Payout details
    """
    try:
        amount_cents = int(amount_usd * 100)

        transfer = stripe.Transfer.create(
            amount=amount_cents,
            currency="usd",
            destination=provider_account_id,
            metadata={
                "node_id": node_id,
                "platform": "mnemo"
            }
        )

        return {
            "success": True,
            "transfer_id": transfer.id,
            "amount": amount_usd,
            "status": "success"
        }

    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": str(e)
        }


async def create_refund(payment_intent_id: str, amount_usd: Optional[Decimal] = None) -> Dict:
    """
    Create a refund

    Args:
        payment_intent_id: Payment intent to refund
        amount_usd: Optional partial refund amount

    Returns:
        Refund details
    """
    try:
        refund_params = {"payment_intent": payment_intent_id}

        if amount_usd:
            refund_params["amount"] = int(amount_usd * 100)

        refund = stripe.Refund.create(**refund_params)

        return {
            "success": True,
            "refund_id": refund.id,
            "amount": refund.amount / 100,
            "status": refund.status
        }

    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_payment_status(payment_intent_id: str) -> Dict:
    """
    Get status of a payment

    Args:
        payment_intent_id: Payment intent ID

    Returns:
        Payment status details
    """
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        return {
            "success": True,
            "status": intent.status,
            "amount": intent.amount / 100,
            "created": intent.created,
            "metadata": intent.metadata
        }

    except stripe.error.StripeError as e:
        return {
            "success": False,
            "error": str(e)
        }
