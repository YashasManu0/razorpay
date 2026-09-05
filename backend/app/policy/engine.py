from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.db.models import MerchantPolicy, Product, Inventory

class PolicyCheckResult(BaseModel):
    allowed: bool
    reason_code: str
    message: str
    policy_id: Optional[str] = None
    policy_version: Optional[int] = None
    applied_rules: Dict[str, Any] = {}

class MerchantPolicyEngine:
    """
    Deterministic Merchant Policy Engine.
    This service is completely decoupled from the LLM and acts as an unbypassable
    security and business constraint layer.
    """
    
    @staticmethod
    def validate_offer(
        policy: MerchantPolicy,
        product: Product,
        inventory: Optional[Inventory],
        offer_price: float,
        current_round: int,
        requested_delivery_days: Optional[int] = None,
        bundle_cost: float = 0.0,
        free_shipping: bool = False
    ) -> PolicyCheckResult:
        """
        Validates whether a proposed offer complies with all merchant business constraints.
        Returns a structured PolicyCheckResult with machine-readable reason code.
        """
        # Extract policy attributes safely with defaults
        max_rounds = policy.max_negotiation_rounds if policy.max_negotiation_rounds is not None else 3
        low_stock_threshold = policy.low_stock_threshold if policy.low_stock_threshold is not None else 5
        low_stock_max_discount = policy.low_stock_max_discount if policy.low_stock_max_discount is not None else 2.0
        aging_threshold_days = policy.aging_threshold_days if policy.aging_threshold_days is not None else 60
        aging_clearance_discount_boost = policy.aging_clearance_discount_boost if policy.aging_clearance_discount_boost is not None else 3.0
        min_margin = policy.min_margin if policy.min_margin is not None else 4000.0
        max_discount_pct = policy.max_discount_pct if policy.max_discount_pct is not None else 8.0
        min_delivery_days = policy.min_delivery_days if policy.min_delivery_days is not None else 2
        allow_free_shipping = policy.allow_free_shipping if policy.allow_free_shipping is not None else True
        allow_warranty_bundle = policy.allow_warranty_bundle if policy.allow_warranty_bundle is not None else True
        allow_accessory_bundle = policy.allow_accessory_bundle if policy.allow_accessory_bundle is not None else True

        # 1. Round Limit Verification
        if current_round > max_rounds:
            return PolicyCheckResult(
                allowed=False,
                reason_code="POLICY_ROUND_LIMIT_EXCEEDED",
                message=f"Negotiation round {current_round} exceeds the merchant limit of {max_rounds} rounds.",
                policy_id=policy.id,
                policy_version=policy.version,
                applied_rules={"max_rounds": max_rounds}
            )
            
        # 2. Inventory Availability Verification
        available_stock = 0
        inventory_age_days = 0
        if inventory:
            qty = inventory.quantity if inventory.quantity is not None else 0
            res_qty = inventory.reserved_quantity if inventory.reserved_quantity is not None else 0
            available_stock = qty - res_qty
            inventory_age_days = inventory.age_days if inventory.age_days is not None else 0
            
        if available_stock <= 0:
            return PolicyCheckResult(
                allowed=False,
                reason_code="POLICY_STOCK_EXHAUSTED",
                message="Cannot generate offer: Inventory is completely out of stock or reserved.",
                policy_id=policy.id,
                policy_version=policy.version,
                applied_rules={"available_stock": available_stock}
            )
            
        # 3. Dynamic Maximum Discount Calculation based on stock & age
        effective_max_discount_pct = max_discount_pct
        
        # Scarcity Rule: If stock is low, restrict discounting
        is_low_stock = available_stock <= low_stock_threshold
        if is_low_stock:
            effective_max_discount_pct = min(effective_max_discount_pct, low_stock_max_discount)
            
        # Aging Clearance Rule: If inventory has aged past threshold, permit clearance discount boost
        is_aging_stock = inventory_age_days >= aging_threshold_days
        if is_aging_stock and not is_low_stock:
            effective_max_discount_pct = effective_max_discount_pct + aging_clearance_discount_boost
            
        # 4. Check Price Floor against base listing price
        discount_amount = product.base_price - offer_price
        discount_pct = (discount_amount / product.base_price) * 100.0 if product.base_price > 0 else 0.0
        
        if discount_pct > effective_max_discount_pct + 0.01:  # small epsilon for float precision
            rule_detail = "low stock conservation" if is_low_stock else "merchant standard policy"
            return PolicyCheckResult(
                allowed=False,
                reason_code="POLICY_DISCOUNT_EXCEEDED",
                message=f"Proposed discount of {discount_pct:.1f}% exceeds effective cap of {effective_max_discount_pct:.1f}% ({rule_detail}).",
                policy_id=policy.id,
                policy_version=policy.version,
                applied_rules={
                    "proposed_discount_pct": round(discount_pct, 2),
                    "effective_max_discount_pct": round(effective_max_discount_pct, 2),
                    "is_low_stock": is_low_stock,
                    "is_aging_stock": is_aging_stock
                }
            )
            
        # 5. Margin Floor Verification
        shipping_cost = product.shipping_cost if product.shipping_cost is not None else 500.0
        cost_price = product.cost_price if product.cost_price is not None else 0.0
        effective_shipping_cost = shipping_cost if free_shipping else 0.0
        total_merchant_cost = cost_price + effective_shipping_cost + bundle_cost
        realized_margin = offer_price - total_merchant_cost
        
        if realized_margin < min_margin - 0.01:
            return PolicyCheckResult(
                allowed=False,
                reason_code="POLICY_MIN_MARGIN_VIOLATED",
                message=f"Realized margin of ₹{realized_margin:,.2f} is below the merchant minimum threshold of ₹{min_margin:,.2f}.",
                policy_id=policy.id,
                policy_version=policy.version,
                applied_rules={
                    "realized_margin": round(realized_margin, 2),
                    "min_margin_required": round(min_margin, 2),
                    "total_merchant_cost": round(total_merchant_cost, 2)
                }
            )
            
        # 6. Delivery Feasibility Verification
        if requested_delivery_days is not None:
            if requested_delivery_days < min_delivery_days:
                return PolicyCheckResult(
                    allowed=False,
                    reason_code="POLICY_DELIVERY_UNACHIEVABLE",
                    message=f"Requested delivery of {requested_delivery_days} days is faster than minimum achievable {min_delivery_days} days.",
                    policy_id=policy.id,
                    policy_version=policy.version,
                    applied_rules={
                        "requested_delivery_days": requested_delivery_days,
                        "min_delivery_days": min_delivery_days
                    }
                )
                
        # 7. Perks validation
        if free_shipping and not allow_free_shipping:
            return PolicyCheckResult(
                allowed=False,
                reason_code="POLICY_FREE_SHIPPING_DISABLED",
                message="Merchant policy does not allow complimentary shipping incentives.",
                policy_id=policy.id,
                policy_version=policy.version
            )
            
        if bundle_cost > 0 and not (allow_warranty_bundle or allow_accessory_bundle):
            return PolicyCheckResult(
                allowed=False,
                reason_code="POLICY_BUNDLES_DISABLED",
                message="Merchant policy does not permit product bundling perks.",
                policy_id=policy.id,
                policy_version=policy.version
            )

        # All policy checks PASSED
        return PolicyCheckResult(
            allowed=True,
            reason_code="POLICY_PERMISSIBLE",
            message="Offer complies with all active merchant business rules.",
            policy_id=policy.id,
            policy_version=policy.version,
            applied_rules={
                "effective_max_discount_pct": round(effective_max_discount_pct, 2),
                "realized_margin": round(realized_margin, 2),
                "is_low_stock": is_low_stock,
                "is_aging_stock": is_aging_stock
            }
        )
