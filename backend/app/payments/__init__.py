from app.config import settings
from app.payments.provider_interface import PaymentProvider, PaymentSession, PaymentStatus
from app.payments.razorpay_provider import RazorpayPaymentProvider
from app.payments.mock_provider import MockSandboxProvider

def get_payment_provider() -> PaymentProvider:
    """Returns the configured PaymentProvider instance."""
    if settings.USE_MOCK_PAYMENTS:
        return MockSandboxProvider()
    return RazorpayPaymentProvider()
