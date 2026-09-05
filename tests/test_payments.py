import pytest
import json
import hmac
import hashlib
from app.payments.mock_provider import MockSandboxProvider

def test_mock_provider_payment_session():
    provider = MockSandboxProvider(secret="test_secret_12345")
    session = provider.create_payment(order_id="ord_test_01", amount=77499.0)
    
    assert session.amount_inr == 77499.0
    assert session.amount_paise == 7749900
    assert session.status == "CREATED"
    assert session.provider_order_id.startswith("order_mock_")

def test_webhook_signature_verification():
    provider = MockSandboxProvider(secret="test_secret_12345")
    payload = json.dumps({"event": "payment.captured", "order_id": "order_123"})
    
    # Compute genuine HMAC-SHA256 signature
    valid_sig = hmac.new(
        key="test_secret_12345".encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    assert provider.verify_webhook(payload, valid_sig) is True
    assert provider.verify_webhook(payload, "invalid_spoofed_signature") is False
