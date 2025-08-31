from typing import List, Optional, Dict, Any
from ..models.commerce import PaymentCreate, PaymentBase, PaymentStatus, PaymentMethod
from ..utils.api_client import get_api_client
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.api = get_api_client()
    
    async def create_payment(self, payment_data: PaymentCreate) -> Optional[PaymentBase]:
        """Process a new payment"""
        try:
            response = await self.api.post(
                "payments/",
                json=payment_data.dict(),
                response_model=PaymentBase
            )
            
            if not response.success:
                logger.error(f"Payment failed: {response.error}")
                return None
                
            return response.data
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            raise
    
    async def get_payment(self, payment_id: str) -> Optional[PaymentBase]:
        """Get payment by ID"""
        try:
            response = await self.api.get(
                f"payments/{payment_id}",
                response_model=PaymentBase
            )
            
            if not response.success:
                logger.warning(f"Payment not found: {payment_id}")
                return None
                
            return response.data
        except Exception as e:
            logger.error(f"Error fetching payment: {str(e)}")
            raise
    
    async def update_payment_status(
        self,
        payment_id: str,
        status: PaymentStatus,
        transaction_id: Optional[str] = None
    ) -> Optional[PaymentBase]:
        """Update payment status"""
        try:
            update_data = {"status": status}
            if transaction_id:
                update_data["transaction_id"] = transaction_id
                
            response = await self.api.patch(
                f"payments/{payment_id}",
                json=update_data,
                response_model=PaymentBase
            )
            
            if not response.success:
                logger.error(f"Failed to update payment: {response.error}")
                return None
                
            return response.data
        except Exception as e:
            logger.error(f"Error updating payment: {str(e)}")
            raise
    
    async def list_payments(
        self,
        order_id: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        method: Optional[PaymentMethod] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PaymentBase]:
        """List payments with optional filters"""
        try:
            params = {"limit": limit, "offset": offset}
            if order_id:
                params["order_id"] = order_id
            if status:
                params["status"] = status
            if method:
                params["method"] = method
                
            response = await self.api.get(
                "payments/",
                params=params,
                response_model=List[PaymentBase]
            )
            
            if not response.success:
                logger.error(f"Failed to list payments: {response.error}")
                return []
                
            return response.data or []
        except Exception as e:
            logger.error(f"Error listing payments: {str(e)}")
            raise
    
    async def process_refund(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> bool:
        """Process a refund for a payment"""
        try:
            refund_data = {}
            if amount is not None:
                refund_data["amount"] = amount
            if reason:
                refund_data["reason"] = reason
                
            response = await self.api.post(
                f"payments/{payment_id}/refund",
                json=refund_data if refund_data else None
            )
            
            if not response.success:
                logger.error(f"Refund failed: {response.error}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            raise

# Singleton instance
payment_service: Optional[PaymentService] = None

def get_payment_service() -> PaymentService:
    """Get or create the payment service instance"""
    global payment_service
    if payment_service is None:
        payment_service = PaymentService()
    return payment_service
