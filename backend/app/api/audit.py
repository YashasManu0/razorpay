from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.db.models import Offer, OfferCandidate, Negotiation, Product, Inventory, MerchantPolicy, AuditLog, Order, Payment

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/explain/{offer_id}")
def explain_offer_pricing(offer_id: str, db: Session = Depends(get_db)):
    """
    Core Hackathon Transparency Feature:
    'WHY DID THE AI OFFER THIS PRICE?'
    Provides the complete, immutable mathematical and policy decision chain.
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer record not found")
        
    negotiation = offer.negotiation
    product = db.query(Product).filter(Product.id == offer.product_id).first()
    policy = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == product.merchant_id, MerchantPolicy.is_active == True).first()
    
    # Evaluated candidates in this round
    candidates = db.query(OfferCandidate).filter(
        OfferCandidate.negotiation_id == negotiation.id,
        OfferCandidate.round_number == offer.round_number
    ).all()
    
    order = db.query(Order).filter(Order.offer_id == offer.id).first()
    payment = db.query(Payment).filter(Payment.order_id == order.id).first() if order else None
    
    chain = {
        "summary": {
            "offer_id": offer.id,
            "product_title": product.title,
            "final_offer_price": offer.offer_price,
            "list_price": offer.list_price,
            "discount_pct": offer.discount_pct,
            "merchant_cost": offer.merchant_cost,
            "merchant_margin": offer.merchant_margin,
            "expected_profit": offer.expected_profit,
            "p_conversion": offer.p_conversion,
            "bandit_action": offer.bandit_action,
            "reason_code": offer.reason_code,
            "created_at": offer.created_at.isoformat()
        },
        "decision_chain_steps": [
            {
                "step_number": 1,
                "title": "Buyer Intent & Explicit Hardware Parsing",
                "description": "Deterministic parser extracted buyer requirements from untrusted natural language query.",
                "details": {
                    "raw_query": negotiation.buyer_initial_query,
                    "extracted_budget": negotiation.buyer_budget,
                    "target_delivery_days": negotiation.buyer_max_delivery_days or 3,
                    "specs_extracted": negotiation.buyer_specs_extracted
                }
            },
            {
                "step_number": 2,
                "title": "Merchant Base Financials & Inventory Snapshot",
                "description": "Retrieved live product costs, listing prices, and inventory age from the transactional database.",
                "details": {
                    "list_price": product.base_price,
                    "unit_procurement_cost": product.cost_price,
                    "available_inventory": product.inventory.quantity - product.inventory.reserved_quantity if product.inventory else 0,
                    "inventory_age_days": product.inventory.age_days if product.inventory else 0,
                    "warehouse": product.inventory.warehouse_location if product.inventory else "BLR-WH-01"
                }
            },
            {
                "step_number": 3,
                "title": "Merchant Policy Constraint Loading",
                "description": "Loaded dynamic merchant business rules from database (never hardcoded in LLM prompts).",
                "details": {
                    "policy_id": policy.id if policy else "default",
                    "policy_version": policy.version if policy else 1,
                    "minimum_margin_required": policy.min_margin if policy else 4000.0,
                    "maximum_allowed_discount_pct": policy.max_discount_pct if policy else 8.0,
                    "max_negotiation_rounds": policy.max_negotiation_rounds if policy else 3,
                    "low_stock_guard_threshold": policy.low_stock_threshold if policy else 5,
                    "aging_clearance_threshold": policy.aging_threshold_days if policy else 60
                }
            },
            {
                "step_number": 4,
                "title": "Candidate Offer Generation & Mathematical Optimization",
                "description": "Pricing engine evaluated multiple permissible candidate strategies, computing P(accept) and Expected Profit = P(accept) * Margin.",
                "details": {
                    "candidates_evaluated": [
                        {
                            "strategy": c.strategy_name,
                            "price": c.candidate_price,
                            "discount_pct": c.discount_pct,
                            "realized_margin": c.calculated_margin,
                            "p_conversion": c.p_conversion,
                            "expected_profit": c.expected_profit,
                            "is_permissible": c.is_permissible,
                            "policy_check": c.policy_reason_code,
                            "is_chosen": c.is_selected
                        }
                        for c in candidates
                    ]
                }
            },
            {
                "step_number": 5,
                "title": "Contextual Bandit Action Selection",
                "description": "The LinUCB bandit selected the optimal permissible action maximizing the exploration-exploitation reward bound.",
                "details": {
                    "chosen_action": offer.bandit_action,
                    "decision_rationale": offer.explanation or "Maximized expected profit across permissible strategies."
                }
            },
            {
                "step_number": 6,
                "title": "Authoritative Payment Authorization",
                "description": "Server-side price lock created for payment provider. Client amounts strictly disregarded.",
                "details": {
                    "order_status": order.status if order else "NOT_ORDERED_YET",
                    "payment_status": payment.status if payment else "NOT_INITIATED",
                    "hmac_signature_verified": payment.is_signature_verified if payment else False
                }
            }
        ]
    }
    return chain

@router.get("/logs")
def list_audit_logs(
    entity_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
        
    logs = q.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "action": l.action,
            "actor": l.actor,
            "details": l.details,
            "timestamp": l.timestamp.isoformat()
        }
        for l in logs
    ]
