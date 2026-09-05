import pytest
from app.db.models import MerchantPolicy, Product, Inventory
from app.policy.engine import MerchantPolicyEngine

@pytest.fixture
def sample_setup():
    policy = MerchantPolicy(
        min_margin=5000.0,
        max_discount_pct=8.0,
        max_negotiation_rounds=3,
        low_stock_threshold=5,
        low_stock_max_discount=2.0,
        aging_threshold_days=60,
        aging_clearance_discount_boost=3.0,
        allow_free_shipping=True,
        min_delivery_days=2
    )
    product = Product(
        base_price=80000.0,
        cost_price=65000.0,
        shipping_cost=500.0
    )
    inventory = Inventory(
        quantity=15,
        reserved_quantity=0,
        age_days=20
    )
    return policy, product, inventory

def test_permissible_offer_passes(sample_setup):
    policy, product, inventory = sample_setup
    # 4% discount: ₹76,800. Margin: ₹76,800 - ₹65,000 = ₹11,800 > ₹5,000.
    res = MerchantPolicyEngine.validate_offer(
        policy=policy,
        product=product,
        inventory=inventory,
        offer_price=76800.0,
        current_round=1
    )
    assert res.allowed is True
    assert res.reason_code == "POLICY_PERMISSIBLE"

def test_margin_floor_violation_blocked(sample_setup):
    policy, product, inventory = sample_setup
    # Offer ₹68,000: Margin = ₹68,000 - ₹65,000 = ₹3,000 < ₹5,000 minimum margin!
    res = MerchantPolicyEngine.validate_offer(
        policy=policy,
        product=product,
        inventory=inventory,
        offer_price=68000.0,
        current_round=1
    )
    assert res.allowed is False
    assert res.reason_code in ("POLICY_MIN_MARGIN_VIOLATED", "POLICY_DISCOUNT_EXCEEDED")

def test_discount_ceiling_blocked(sample_setup):
    policy, product, inventory = sample_setup
    # 12% discount: ₹70,400. Exceeds max_discount_pct of 8%.
    res = MerchantPolicyEngine.validate_offer(
        policy=policy,
        product=product,
        inventory=inventory,
        offer_price=70400.0,
        current_round=1
    )
    assert res.allowed is False
    assert res.reason_code == "POLICY_DISCOUNT_EXCEEDED"

def test_low_stock_scarcity_constraint(sample_setup):
    policy, product, inventory = sample_setup
    # Set inventory to scarce level: 3 units <= threshold 5
    inventory.quantity = 3
    # 4% discount should now be blocked because low stock caps discount to 2%
    res = MerchantPolicyEngine.validate_offer(
        policy=policy,
        product=product,
        inventory=inventory,
        offer_price=76800.0,  # 4% discount
        current_round=1
    )
    assert res.allowed is False
    assert res.reason_code == "POLICY_DISCOUNT_EXCEEDED"

def test_stock_exhausted_blocked(sample_setup):
    policy, product, inventory = sample_setup
    inventory.quantity = 2
    inventory.reserved_quantity = 2  # 0 available
    res = MerchantPolicyEngine.validate_offer(
        policy=policy,
        product=product,
        inventory=inventory,
        offer_price=80000.0,
        current_round=1
    )
    assert res.allowed is False
    assert res.reason_code == "POLICY_STOCK_EXHAUSTED"

def test_round_limit_exceeded(sample_setup):
    policy, product, inventory = sample_setup
    res = MerchantPolicyEngine.validate_offer(
        policy=policy,
        product=product,
        inventory=inventory,
        offer_price=80000.0,
        current_round=4  # Exceeds max 3 rounds
    )
    assert res.allowed is False
    assert res.reason_code == "POLICY_ROUND_LIMIT_EXCEEDED"
