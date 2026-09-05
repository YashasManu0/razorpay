from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.db.models import MerchantPolicy, Product, Inventory
from app.policy.engine import MerchantPolicyEngine
from app.ml.conversion_model import conversion_model
from app.ml.bandit import bandit

class CandidateOffer(BaseModel):
    strategy_name: str
    offer_price: float
    discount_pct: float
    discount_amount: float
    free_shipping: bool = False
    warranty_months: int = 12
    bundle_name: Optional[str] = None
    bundle_cost: float = 0.0
    bundle_retail_value: float = 0.0
    total_cost: float
    realized_margin: float
    p_conversion: float
    expected_profit: float
    is_permissible: bool
    policy_reason_code: str
    policy_message: str

class PricingEvaluationResult(BaseModel):
    selected_offer: CandidateOffer
    all_candidates: List[CandidateOffer]
    permissible_count: int
    optimal_reason: str
    bandit_action: str
    audit_snapshot: Dict[str, Any]

class PricingEngine:
    """
    Independent Python Pricing Engine.
    Evaluates candidate offer strategies, computes purchase probabilities and expected profits:
        expected_profit = purchase_probability * (offer_price - merchant_cost)
    and selects the optimal offer maximizing expected merchant profit while strictly complying
    with merchant policy constraints.
    """
    
    @classmethod
    def evaluate_offers(
        cls,
        policy: MerchantPolicy,
        product: Product,
        inventory: Optional[Inventory],
        buyer_budget: float,
        current_round: int = 1,
        product_relevance: float = 0.90,
        urgency_score: float = 0.50,
        delivery_days: int = 3,
        discount_sensitivity: float = 0.65,
        counter_proposal_price: Optional[float] = None
    ) -> PricingEvaluationResult:
        
        candidates: List[CandidateOffer] = []
        base_price = product.base_price
        
        # 1. Generate standard candidate strategies
        strategies = [
            {"name": "FULL_PRICE", "pct": 0.0, "free_shipping": False, "warranty": 12, "bundle": None, "b_cost": 0.0, "b_val": 0.0},
            {"name": "DISCOUNT_2", "pct": 2.0, "free_shipping": False, "warranty": 12, "bundle": None, "b_cost": 0.0, "b_val": 0.0},
            {"name": "DISCOUNT_4", "pct": 4.0, "free_shipping": False, "warranty": 12, "bundle": None, "b_cost": 0.0, "b_val": 0.0},
            {"name": "DISCOUNT_6", "pct": 6.0, "free_shipping": False, "warranty": 12, "bundle": None, "b_cost": 0.0, "b_val": 0.0},
        ]
        
        if policy.max_discount_pct >= 8.0:
            strategies.append({"name": "DISCOUNT_8", "pct": 8.0, "free_shipping": False, "warranty": 12, "bundle": None, "b_cost": 0.0, "b_val": 0.0})
            
        if policy.allow_free_shipping:
            strategies.append({"name": "FREE_SHIPPING", "pct": 0.0, "free_shipping": True, "warranty": 12, "bundle": None, "b_cost": 0.0, "b_val": 0.0})
            
        if policy.allow_warranty_bundle:
            strategies.append({
                "name": "WARRANTY",
                "pct": 1.5,
                "free_shipping": False,
                "warranty": 24,
                "bundle": "2-Year Extended Care",
                "b_cost": 450.0,
                "b_val": 2999.0
            })
            
        if policy.allow_accessory_bundle:
            strategies.append({
                "name": "BUNDLE",
                "pct": 2.0,
                "free_shipping": True,
                "warranty": 12,
                "bundle": "Gaming Pro Accessory Kit",
                "b_cost": 700.0,
                "b_val": 3499.0
            })
            
        # If buyer made an explicit counter-proposal, evaluate it directly as a candidate!
        if counter_proposal_price is not None:
            c_discount_pct = max(0.0, round(((base_price - counter_proposal_price) / base_price) * 100.0, 2))
            strategies.append({
                "name": "BUYER_COUNTER_PROPOSAL",
                "pct": c_discount_pct,
                "explicit_price": counter_proposal_price,
                "free_shipping": False,
                "warranty": 12,
                "bundle": None,
                "b_cost": 0.0,
                "b_val": 0.0
            })
            
        # 2. Evaluate each strategy
        for strat in strategies:
            if "explicit_price" in strat:
                price = float(strat["explicit_price"])
                discount_pct = strat["pct"]
            else:
                discount_pct = strat["pct"]
                price = round(base_price * (1.0 - (discount_pct / 100.0)), 2)
                
            discount_amount = round(base_price - price, 2)
            free_shipping = strat["free_shipping"]
            bundle_cost = strat["b_cost"]
            
            # Run deterministic Policy Check
            policy_res = MerchantPolicyEngine.validate_offer(
                policy=policy,
                product=product,
                inventory=inventory,
                offer_price=price,
                current_round=current_round,
                requested_delivery_days=delivery_days,
                bundle_cost=bundle_cost,
                free_shipping=free_shipping
            )
            
            shipping_subsidy = product.shipping_cost if free_shipping else 0.0
            total_cost = round(product.cost_price + shipping_subsidy + bundle_cost, 2)
            margin = round(price - total_cost, 2)
            
            if not policy_res.allowed:
                # Disallowed by policy
                candidate = CandidateOffer(
                    strategy_name=strat["name"],
                    offer_price=price,
                    discount_pct=discount_pct,
                    discount_amount=discount_amount,
                    free_shipping=free_shipping,
                    warranty_months=strat["warranty"],
                    bundle_name=strat["bundle"],
                    bundle_cost=bundle_cost,
                    bundle_retail_value=strat["b_val"],
                    total_cost=total_cost,
                    realized_margin=margin,
                    p_conversion=0.0,
                    expected_profit=0.0,
                    is_permissible=False,
                    policy_reason_code=policy_res.reason_code,
                    policy_message=policy_res.message
                )
            else:
                # Permissible: compute ML purchase probability
                features = {
                    "base_price": base_price,
                    "offer_price": price,
                    "discount_pct": discount_pct,
                    "buyer_budget": buyer_budget,
                    "product_relevance": product_relevance,
                    "inventory_quantity": inventory.quantity if inventory else 10,
                    "inventory_age_days": inventory.age_days if inventory else 15,
                    "delivery_days": delivery_days,
                    "urgency_score": urgency_score,
                    "negotiation_round": current_round,
                    "free_shipping": free_shipping,
                    "warranty_months": strat["warranty"],
                    "category": product.category,
                    "previous_outcome": "none"
                }
                p_buy = conversion_model.predict_probability(features)
                exp_profit = round(p_buy * margin, 2)
                
                candidate = CandidateOffer(
                    strategy_name=strat["name"],
                    offer_price=price,
                    discount_pct=discount_pct,
                    discount_amount=discount_amount,
                    free_shipping=free_shipping,
                    warranty_months=strat["warranty"],
                    bundle_name=strat["bundle"],
                    bundle_cost=bundle_cost,
                    bundle_retail_value=strat["b_val"],
                    total_cost=total_cost,
                    realized_margin=margin,
                    p_conversion=p_buy,
                    expected_profit=exp_profit,
                    is_permissible=True,
                    policy_reason_code="POLICY_PERMISSIBLE",
                    policy_message="Permissible under all merchant constraints"
                )
                
            candidates.append(candidate)
            
        # 3. Filter permissible candidates
        permissible_candidates = [c for c in candidates if c.is_permissible]
        
        if not permissible_candidates:
            # Fallback safest offer: Base Price with 0 discount
            # If even base price violates policy (e.g. out of stock), return the best informative block
            disallowed_stock = next((c for c in candidates if c.policy_reason_code == "POLICY_STOCK_EXHAUSTED"), None)
            selected = disallowed_stock or candidates[0]
            bandit_action = "BLOCKED"
            optimal_reason = f"No offer met merchant policy constraints: {selected.policy_message}"
        else:
            # Check Contextual Bandit selection
            context = {
                "base_price": base_price,
                "buyer_budget": buyer_budget,
                "product_relevance": product_relevance,
                "inventory_quantity": inventory.quantity if inventory else 10,
                "inventory_age_days": inventory.age_days if inventory else 15,
                "urgency_score": urgency_score,
                "negotiation_round": current_round,
                "discount_sensitivity": discount_sensitivity
            }
            permissible_names = [c.strategy_name for c in permissible_candidates if c.strategy_name in bandit.actions]
            
            bandit_res = bandit.select_action(context, permissible_actions=permissible_names)
            ucb_scores = bandit_res.get("ucb_scores", {})
            
            def candidate_score(c: CandidateOffer) -> float:
                # Primary objective: Expected Merchant Profit = P(accept) * Margin
                # Plus LinUCB exploration bonus
                ucb_bonus = ucb_scores.get(c.strategy_name, 0.0)
                return c.expected_profit + (ucb_bonus * 300.0)
                
            selected = max(permissible_candidates, key=candidate_score)
            bandit_action = selected.strategy_name
            optimal_reason = (
                f"Selected '{selected.strategy_name}' maximizing Expected Merchant Profit: "
                f"P(accept)={selected.p_conversion:.1%} × Margin(₹{selected.realized_margin:,.2f}) = ₹{selected.expected_profit:,.2f} "
                f"(LinUCB action: {bandit_action})."
            )

        audit_snapshot = {
            "product_id": product.id,
            "product_title": product.title,
            "list_price": base_price,
            "merchant_cost": product.cost_price,
            "buyer_budget": buyer_budget,
            "current_round": current_round,
            "total_candidates": len(candidates),
            "permissible_candidates": len(permissible_candidates),
            "selected_strategy": selected.strategy_name,
            "selected_price": selected.offer_price,
            "expected_profit": selected.expected_profit,
            "p_conversion": selected.p_conversion,
            "realized_margin": selected.realized_margin
        }

        return PricingEvaluationResult(
            selected_offer=selected,
            all_candidates=candidates,
            permissible_count=len(permissible_candidates),
            optimal_reason=optimal_reason,
            bandit_action=bandit_action,
            audit_snapshot=audit_snapshot
        )
