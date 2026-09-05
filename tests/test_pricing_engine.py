import pytest
from app.db.models import MerchantPolicy, Product, Inventory
from app.pricing.engine import PricingEngine

def test_pricing_engine_evaluates_candidates():
    policy = MerchantPolicy(
        min_margin=4000.0,
        max_discount_pct=8.0,
        max_negotiation_rounds=3,
        low_stock_threshold=5,
        allow_free_shipping=True,
        allow_warranty_bundle=True,
        allow_accessory_bundle=True
    )
    product = Product(
        base_price=80000.0,
        cost_price=64000.0,
        shipping_cost=500.0,
        category="laptops",
        title="Test Gaming Laptop"
    )
    inventory = Inventory(quantity=15, reserved_quantity=0, age_days=20)
    
    result = PricingEngine.evaluate_offers(
        policy=policy,
        product=product,
        inventory=inventory,
        buyer_budget=76000.0,
        current_round=1
    )
    
    assert len(result.all_candidates) >= 5
    assert result.permissible_count > 0
    assert result.selected_offer.is_permissible is True
    assert result.selected_offer.realized_margin >= policy.min_margin
    assert result.selected_offer.expected_profit > 0.0

def test_pricing_engine_rejects_adversarial_counter():
    policy = MerchantPolicy(
        min_margin=5000.0,
        max_discount_pct=8.0,
        max_negotiation_rounds=3
    )
    product = Product(
        base_price=80000.0,
        cost_price=65000.0,
        shipping_cost=500.0,
        category="laptops",
        title="Test Gaming Laptop"
    )
    inventory = Inventory(quantity=10, reserved_quantity=0, age_days=15)
    
    # Buyer counter ₹55,000 (huge loss)
    result = PricingEngine.evaluate_offers(
        policy=policy,
        product=product,
        inventory=inventory,
        buyer_budget=55000.0,
        current_round=2,
        counter_proposal_price=55000.0
    )
    
    counter_cand = next((c for c in result.all_candidates if c.strategy_name == "BUYER_COUNTER_PROPOSAL"), None)
    assert counter_cand is not None
    assert counter_cand.is_permissible is False
    assert result.selected_offer.is_permissible is True
    assert result.selected_offer.offer_price >= 73600.0  # Max 8% discount floor
