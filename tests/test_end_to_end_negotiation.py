import pytest
from app.db.session import SessionLocal
from app.api.negotiations import start_negotiation, send_negotiation_message, StartNegotiationPayload, SendMessagePayload
from app.api.payments import create_payment_session, simulate_successful_payment, CreatePaymentSessionPayload, SimulatePaymentPayload
from app.db.models import Order, Payment, Negotiation

def test_full_negotiation_and_payment_flow():
    db = SessionLocal()
    
    # 1. Buyer starts negotiation with explicit specs
    start_res = start_negotiation(
        payload=StartNegotiationPayload(
            query="I need a gaming laptop under ₹80,000, 32GB RAM, 1TB SSD, and delivery within 3 days.",
            buyer_name="Test Shopping Agent",
            buyer_email="agent.test@commerce.ai"
        ),
        db=db
    )
    
    negotiation_id = start_res["negotiation_id"]
    assert negotiation_id is not None
    assert start_res["product"] is not None
    assert start_res["offer"] is not None
    assert start_res["offer"]["offer_price"] <= 85000.0
    
    # 2. Buyer counters with ₹76,000
    counter_res = send_negotiation_message(
        negotiation_id=negotiation_id,
        payload=SendMessagePayload(message="Can you do ₹76,000?", counter_price=76000.0),
        db=db
    )
    
    assert counter_res["round"] == 2
    assert counter_res["offer"] is not None
    assert counter_res["offer"]["offer_price"] <= 80000.0  # Conceded under buyer budget!
    assert counter_res["offer"]["offer_price"] >= 72000.0  # Respects policy margin floor!
    
    # 3. Buyer accepts the offer
    accept_res = send_negotiation_message(
        negotiation_id=negotiation_id,
        payload=SendMessagePayload(message="I accept this deal. Let's proceed to payment!"),
        db=db
    )
    
    assert accept_res["status"] == "ACCEPTED"
    order_id = accept_res["order_id"]
    assert order_id is not None
    
    # 4. Create authoritative payment session
    payment_res = create_payment_session(
        payload=CreatePaymentSessionPayload(order_id=order_id),
        idempotency_key_header=f"test_idemp_{order_id}",
        db=db
    )
    
    assert payment_res["status"] == "PENDING"
    assert payment_res["amount_inr"] == accept_res["offer"]["price"]
    
    # 5. Simulate verified payment capture
    sim_res = simulate_successful_payment(
        payload=SimulatePaymentPayload(order_id=order_id, method="upi"),
        db=db
    )
    
    assert sim_res["order_status"] == "PAID"
    assert sim_res["signature_verified"] is True
    
    # Verify final database state
    order = db.query(Order).filter(Order.id == order_id).first()
    assert order.status == "PAID"
    
    negotiation = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    assert negotiation.status == "COMPLETED"
    
    db.close()
