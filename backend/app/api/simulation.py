import random
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import Product, MerchantPolicy, Inventory
from app.policy.engine import MerchantPolicyEngine
from app.ml.bandit import bandit, BANDIT_ACTIONS
from app.ml.conversion_model import conversion_model

router = APIRouter(prefix="/simulation", tags=["simulation"])

class RunSimulationPayload(BaseModel):
    n_trials: int = 100
    reset_bandit: bool = False

@router.get("/state")
def get_simulation_state():
    """Returns current learning curve and trial history of the LinUCB bandit."""
    return {
        "total_trials": bandit.total_trials,
        "cumulative_profit": round(bandit.cumulative_profit, 2),
        "history": bandit.history[-100:],  # last 100 trials
        "actions": BANDIT_ACTIONS
    }

@router.post("/run")
def run_bandit_simulation(payload: RunSimulationPayload, db: Session = Depends(get_db)):
    """
    Executes a live simulation loop of repeated autonomous buyer-merchant negotiations.
    Judges can watch the LinUCB Contextual Bandit explore and exploit to maximize profit
    while the Merchant Policy Engine filters out non-compliant actions.
    """
    if payload.reset_bandit:
        bandit.history.clear()
        bandit.cumulative_profit = 0.0
        bandit.total_trials = 0
        bandit.A = {a: np.identity(bandit.d) for a in bandit.actions}
        bandit.b = {a: np.zeros((bandit.d, 1)) for a in bandit.actions}

    products = db.query(Product).filter(Product.is_active == True).all()
    if not products:
        return {"error": "No products found in catalog. Seed data first."}

    policy = db.query(MerchantPolicy).first()
    if not policy:
        policy = MerchantPolicy(merchant_id=products[0].merchant_id)

    trials_run = 0
    trial_records = []

    for _ in range(payload.n_trials):
        product = random.choice(products)
        inv = product.inventory
        
        # Simulate buyer context
        budget_discount = random.uniform(0.0, 0.12)
        buyer_budget = round(product.base_price * (1.0 - budget_discount), 2)
        urgency = random.uniform(0.3, 0.9)
        round_num = random.choice([1, 2, 3])
        sensitivity = random.uniform(0.4, 0.95)
        
        context = {
            "base_price": product.base_price,
            "buyer_budget": buyer_budget,
            "product_relevance": random.uniform(0.8, 0.98),
            "inventory_quantity": inv.quantity if inv else 10,
            "inventory_age_days": inv.age_days if inv else 20,
            "urgency_score": urgency,
            "negotiation_round": round_num,
            "discount_sensitivity": sensitivity
        }
        
        # 1. Deterministic Policy Engine filters permissible actions
        permissible_actions = []
        action_offer_details = {}
        
        for action in bandit.actions:
            discount_pct = 0.0
            free_shipping = False
            bundle_cost = 0.0
            
            if action == "FULL_PRICE":
                discount_pct = 0.0
            elif action == "DISCOUNT_2":
                discount_pct = 2.0
            elif action == "DISCOUNT_4":
                discount_pct = 4.0
            elif action == "DISCOUNT_6":
                discount_pct = 6.0
            elif action == "FREE_SHIPPING":
                discount_pct = 0.0
                free_shipping = True
            elif action == "WARRANTY":
                discount_pct = 1.5
                bundle_cost = 450.0
            elif action == "BUNDLE":
                discount_pct = 2.0
                free_shipping = True
                bundle_cost = 700.0

            cand_price = round(product.base_price * (1.0 - discount_pct / 100.0), 2)
            
            check = MerchantPolicyEngine.validate_offer(
                policy=policy,
                product=product,
                inventory=inv,
                offer_price=cand_price,
                current_round=round_num,
                requested_delivery_days=3,
                bundle_cost=bundle_cost,
                free_shipping=free_shipping
            )
            
            if check.allowed:
                permissible_actions.append(action)
                margin = cand_price - (product.cost_price + (product.shipping_cost if free_shipping else 0.0) + bundle_cost)
                action_offer_details[action] = {
                    "price": cand_price,
                    "discount_pct": discount_pct,
                    "margin": margin,
                    "free_shipping": free_shipping,
                    "bundle_cost": bundle_cost
                }

        if not permissible_actions:
            permissible_actions = ["FULL_PRICE"]
            action_offer_details["FULL_PRICE"] = {
                "price": product.base_price,
                "discount_pct": 0.0,
                "margin": product.base_price - product.cost_price,
                "free_shipping": False,
                "bundle_cost": 0.0
            }

        # 2. Bandit selects action among permissible ones
        selection = bandit.select_action(context, permissible_actions=permissible_actions)
        chosen_action = selection["selected_action"]
        chosen_details = action_offer_details[chosen_action]

        # 3. Simulate buyer acceptance via ML model probability
        features = {
            "base_price": product.base_price,
            "offer_price": chosen_details["price"],
            "discount_pct": chosen_details["discount_pct"],
            "buyer_budget": buyer_budget,
            "product_relevance": context["product_relevance"],
            "inventory_quantity": context["inventory_quantity"],
            "inventory_age_days": context["inventory_age_days"],
            "delivery_days": 3,
            "urgency_score": urgency,
            "negotiation_round": round_num,
            "free_shipping": chosen_details["free_shipping"],
            "warranty_months": 24 if chosen_action == "WARRANTY" else 12,
            "category": product.category,
            "previous_outcome": "none"
        }
        
        p_accept = conversion_model.predict_probability(features)
        accepted = bool(random.random() < p_accept)
        
        realized_profit = chosen_details["margin"] if accepted else 0.0
        normalized_reward = (chosen_details["margin"] / 10000.0) if accepted else 0.0
        
        # 4. Update bandit online
        bandit.update(
            action=chosen_action,
            context=context,
            reward=normalized_reward,
            profit=realized_profit,
            accepted=accepted
        )
        
        trials_run += 1
        trial_records.append({
            "trial": bandit.total_trials,
            "action": chosen_action,
            "price": chosen_details["price"],
            "margin": round(chosen_details["margin"], 2),
            "p_accept": round(p_accept, 3),
            "accepted": accepted,
            "realized_profit": round(realized_profit, 2),
            "cumulative_profit": round(bandit.cumulative_profit, 2)
        })

    return {
        "trials_executed": trials_run,
        "total_lifetime_trials": bandit.total_trials,
        "cumulative_profit": round(bandit.cumulative_profit, 2),
        "recent_trials": trial_records[-20:],
        "overall_acceptance_rate": round(sum(1 for t in trial_records if t["accepted"]) / max(len(trial_records), 1) * 100.0, 1)
    }
