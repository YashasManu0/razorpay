import hmac
import hashlib
import json
import razorpay
from typing import Dict, Any, Optional
from app.config import settings
from app.payments.provider_interface import PaymentProvider, PaymentSession, PaymentStatus

class RazorpayPaymentProvider(PaymentProvider):
    """
    Razorpay Sandbox / Production Gateway Adapter.
    Uses official Razorpay Client and enforces server-side amount integrity and HMAC-SHA256 signatures.
    """
    
    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        self.key_id = key_id or settings.RAZORPAY_KEY_ID
        self.key_secret = key_secret or settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_payment(
        self,
        order_id: str,
        amount: float,
        currency: str = "INR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentSession:
        # Razorpay expects amounts in the smallest currency sub-unit (paise for INR)
        amount_paise = int(round(amount * 100))
        
        payload = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": order_id[:40],
            "notes": metadata or {"order_id": order_id}
        }
        
        try:
            rzp_order = self.client.order.create(data=payload)
            return PaymentSession(
                provider="razorpay",
                provider_order_id=rzp_order["id"],
                amount_inr=amount,
                amount_paise=amount_paise,
                currency=currency,
                status=rzp_order.get("status", "created").upper(),
                metadata={"receipt": order_id, "notes": payload["notes"]}
            )
        except Exception as e:
            # Re-raise or wrap cleanly
            raise RuntimeError(f"Razorpay order creation failed: {str(e)}")

    def get_payment(self, payment_id: str) -> PaymentStatus:
        try:
            payment = self.client.payment.fetch(payment_id)
            status_map = {
                "authorized": "AUTHORIZED",
                "captured": "SUCCESS",
                "failed": "FAILED",
                "refunded": "REFUNDED"
            }
            mapped_status = status_map.get(payment.get("status"), "PENDING")
            return PaymentStatus(
                provider_payment_id=payment["id"],
                provider_order_id=payment.get("order_id", ""),
                amount_inr=float(payment["amount"]) / 100.0,
                currency=payment.get("currency", "INR"),
                status=mapped_status,
                method=payment.get("method", "card"),
                email=payment.get("email"),
                contact=payment.get("contact"),
                raw_response=payment
            )
        except Exception as e:
            raise RuntimeError(f"Razorpay payment fetch failed for {payment_id}: {str(e)}")

    def verify_webhook(
        self,
        payload_body: str,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """
        Verifies the cryptographic HMAC-SHA256 signature sent by Razorpay webhook headers.
        `X-Razorpay-Signature` = HMAC_SHA256(payload_body, webhook_secret)
        """
        webhook_sec = secret or self.webhook_secret
        if not webhook_sec or not signature:
            return False
            
        try:
            expected_signature = hmac.new(
                key=webhook_sec.encode("utf-8"),
                msg=payload_body.encode("utf-8"),
                digestmod=hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False

    def capture_payment(self, payment_id: str, amount: float, currency: str = "INR") -> bool:
        amount_paise = int(round(amount * 100))
        try:
            res = self.client.payment.capture(payment_id, amount_paise, {"currency": currency})
            return res.get("status") == "captured"
        except Exception:
            return False

    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> bool:
        try:
            data = {}
            if amount is not None:
                data["amount"] = int(round(amount * 100))
            res = self.client.payment.refund(payment_id, data)
            return res.get("status") in ("processed", "refunded")
        except Exception:
            return False
