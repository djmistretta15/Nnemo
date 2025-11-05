"""
Crypto payment verification (Ethereum & Solana)
"""

from web3 import Web3
from typing import Dict, Optional
from decimal import Decimal
from app.config import settings
import requests


class CryptoPaymentHandler:
    """Handle crypto payment verification"""

    def __init__(self):
        # Ethereum Web3 connection
        if settings.ETH_RPC_URL:
            self.eth_w3 = Web3(Web3.HTTPProvider(settings.ETH_RPC_URL))
        else:
            self.eth_w3 = None

        # Solana RPC URL
        self.sol_rpc_url = settings.SOL_RPC_URL

    async def verify_ethereum_payment(
        self,
        tx_hash: str,
        expected_amount: Decimal,
        recipient_address: str
    ) -> Dict:
        """
        Verify Ethereum payment transaction

        Args:
            tx_hash: Transaction hash
            expected_amount: Expected amount in ETH
            recipient_address: Expected recipient address

        Returns:
            Verification result
        """
        if not self.eth_w3:
            return {
                "success": False,
                "error": "Ethereum RPC not configured"
            }

        try:
            # Get transaction
            tx = self.eth_w3.eth.get_transaction(tx_hash)

            if not tx:
                return {
                    "success": False,
                    "error": "Transaction not found"
                }

            # Verify recipient
            if tx['to'].lower() != recipient_address.lower():
                return {
                    "success": False,
                    "error": "Recipient address mismatch"
                }

            # Verify amount
            tx_amount = Web3.from_wei(tx['value'], 'ether')
            expected_wei = Web3.to_wei(float(expected_amount), 'ether')

            if tx['value'] < expected_wei:
                return {
                    "success": False,
                    "error": f"Insufficient amount. Expected: {expected_amount} ETH, Got: {tx_amount} ETH"
                }

            # Check confirmations
            current_block = self.eth_w3.eth.block_number
            tx_block = tx['blockNumber']
            confirmations = current_block - tx_block if tx_block else 0

            return {
                "success": True,
                "tx_hash": tx_hash,
                "amount": float(tx_amount),
                "confirmations": confirmations,
                "from": tx['from'],
                "to": tx['to'],
                "block": tx_block,
                "verified": confirmations >= 3  # Require 3 confirmations
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def verify_solana_payment(
        self,
        tx_signature: str,
        expected_amount: Decimal,
        recipient_address: str
    ) -> Dict:
        """
        Verify Solana payment transaction

        Args:
            tx_signature: Transaction signature
            expected_amount: Expected amount in SOL
            recipient_address: Expected recipient address

        Returns:
            Verification result
        """
        if not self.sol_rpc_url:
            return {
                "success": False,
                "error": "Solana RPC not configured"
            }

        try:
            # Get transaction via RPC
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    tx_signature,
                    {"encoding": "json", "maxSupportedTransactionVersion": 0}
                ]
            }

            response = requests.post(self.sol_rpc_url, json=payload, timeout=10)
            data = response.json()

            if 'error' in data:
                return {
                    "success": False,
                    "error": data['error']['message']
                }

            tx = data.get('result')
            if not tx:
                return {
                    "success": False,
                    "error": "Transaction not found"
                }

            # Extract transaction details
            # Note: This is simplified - production would need more robust parsing
            meta = tx.get('meta', {})
            post_balances = meta.get('postBalances', [])
            pre_balances = meta.get('preBalances', [])

            # Calculate amount transferred (in lamports, 1 SOL = 1e9 lamports)
            if len(post_balances) >= 2 and len(pre_balances) >= 2:
                amount_lamports = post_balances[1] - pre_balances[1]
                amount_sol = amount_lamports / 1e9

                if amount_sol >= float(expected_amount):
                    return {
                        "success": True,
                        "tx_signature": tx_signature,
                        "amount": amount_sol,
                        "verified": True,
                        "block": tx.get('slot')
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Insufficient amount. Expected: {expected_amount} SOL, Got: {amount_sol} SOL"
                    }
            else:
                return {
                    "success": False,
                    "error": "Could not parse transaction balances"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_eth_address_balance(self, address: str) -> Dict:
        """Get Ethereum address balance"""
        if not self.eth_w3:
            return {"success": False, "error": "Ethereum RPC not configured"}

        try:
            balance_wei = self.eth_w3.eth.get_balance(address)
            balance_eth = Web3.from_wei(balance_wei, 'ether')

            return {
                "success": True,
                "address": address,
                "balance": float(balance_eth),
                "currency": "ETH"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_sol_address_balance(self, address: str) -> Dict:
        """Get Solana address balance"""
        if not self.sol_rpc_url:
            return {"success": False, "error": "Solana RPC not configured"}

        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [address]
            }

            response = requests.post(self.sol_rpc_url, json=payload, timeout=10)
            data = response.json()

            if 'error' in data:
                return {"success": False, "error": data['error']['message']}

            balance_lamports = data['result']['value']
            balance_sol = balance_lamports / 1e9

            return {
                "success": True,
                "address": address,
                "balance": balance_sol,
                "currency": "SOL"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global handler instance
crypto_handler = CryptoPaymentHandler()
