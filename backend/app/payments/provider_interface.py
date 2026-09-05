from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class PaymentSession(BaseModel):
    provider: str
    provider_order_id: str
    provider_payment_id: Optional[str] = None
    amount_inr: float
    amount_paise: int
    currency: str = "INR"
    status: str = "CREATED"  # CREATED, AUTHORIZED, CAPTURED, FAILED
    checkout_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class PaymentStatus(BaseModel):
    provider_payment_id: str
    provider_order_id: str
    amount_inr: float
    currency: str
    status: str  # PENDING, SUCCESS, FAILED, REFUNDED
    method: Optional[str] = "upi"  # upi, card, netbanking
    email: Optional[str] = None
    contact: Optional[str] = None
    created_at: Optional[str] = None
    raw_response: Dict[str, Any] = {}

class PaymentProvider(ABC):
    """
    Authoritative Payment Provider Abstraction.
    All financial amounts are strictly dictated by the backend order database.
    """
    
    @abstractmethod
    def create_payment(
        self,
        order_id: str,
        amount: float,
        currency: str = "INR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentSession:
        """Create a payment session or order on the provider gateway."""
        pass

    @abstractmethod
    def get_payment(self, payment_id: str) -> PaymentStatus:
        """Fetch authoritative payment status from the gateway."""
        pass

    @abstractmethod
    def verify_webhook(
        self,
        payload_body: str,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """Cryptographically verify webhook authenticity via HMAC-SHA256 signature."""
        pass

    @abstractmethod
    def capture_payment(self, payment_id: str, amount: float, currency: str = "INR") -> bool:
        """Capture an authorized payment."""
        pass

    @abstractmethod
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> bool:
        """Refund a payment partially or fully."""
        pass
