from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db.models import Negotiation, NegotiationMessage, Buyer, Merchant, Product, Offer, OfferCandidate, Order
from app.agent.negotiator_agent import merchant_agent
from app.config import settings

router = APIRouter(prefix="/negotiations", tags=["negotiations"])

class StartNegotiationPayload(BaseModel):
    query: str
    buyer_name: Optional[str] = "Shopping Agent Alpha"
    buyer_email: Optional[str] = "agent.alpha@commerce.ai"
    merchant_id: Optional[str] = None

class SendMessagePayload(BaseModel):
    message: str
    counter_price: Optional[float] = None

@router.get("/")
def list_negotiations(
    merchant_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 25,
    db: Session = Depends(get_db)
):
    q = db.query(Negotiation)
    if merchant_id:
        q = q.filter(Negotiation.merchant_id == merchant_id)
    if status:
        q = q.filter(Negotiation.status == status)
        
    items = q.order_by(Negotiation.updated_at.desc()).limit(limit).all()
    results = []
    for n in items:
        p = n.product
        active_offer = db.query(Offer).filter(Offer.id == n.active_offer_id).first() if n.active_offer_id else None
        results.append({
            "id": n.id,
            "status": n.status,
            "current_round": n.current_round,
            "max_rounds": n.max_rounds,
            "buyer_name": n.buyer.name if n.buyer else "Anonymous Buyer",
            "product_title": p.title if p else "Searching...",
            "product_category": p.category if p else None,
            "list_price": p.base_price if p else None,
            "active_offer_price": active_offer.offer_price if active_offer else None,
            "discount_pct": active_offer.discount_pct if active_offer else 0.0,
            "expected_profit": active_offer.expected_profit if active_offer else 0.0,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "updated_at": n.updated_at.isoformat() if n.updated_at else None
        })
    return results

@router.post("/start")
def start_negotiation(payload: StartNegotiationPayload, db: Session = Depends(get_db)):
    # 1. Get or create buyer
    buyer = db.query(Buyer).filter(Buyer.email == payload.buyer_email).first()
    if not buyer:
        buyer = Buyer(name=payload.buyer_name, email=payload.buyer_email, is_agent=True)
        db.add(buyer)
        db.commit()
        db.refresh(buyer)
        
    # 2. Identify merchant
    merchant = None
    if payload.merchant_id:
        merchant = db.query(Merchant).filter(Merchant.id == payload.merchant_id).first()
    if not merchant:
        merchant = db.query(Merchant).first()
        if not merchant:
            raise HTTPException(status_code=400, detail="No merchant found in system. Please run seed script first.")
            
    # 3. Create Negotiation record
    expires_at = datetime.utcnow() + timedelta(seconds=settings.OFFER_TTL_SECONDS)
    negotiation = Negotiation(
        buyer_id=buyer.id,
        merchant_id=merchant.id,
        status="INITIATED",
        buyer_initial_query=payload.query,
        current_round=1,
        max_rounds=3,
        expires_at=expires_at
    )
    db.add(negotiation)
    db.commit()
    db.refresh(negotiation)
    
    # 4. Process initial turn through Merchant AI Agent
    result = merchant_agent.process_buyer_turn(
        db=db,
        negotiation=negotiation,
        buyer_message_text=payload.query
    )
    
    return result

@router.post("/{negotiation_id}/message")
def send_negotiation_message(
    negotiation_id: str,
    payload: SendMessagePayload,
    db: Session = Depends(get_db)
):
    negotiation = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
        
    if negotiation.status in ("COMPLETED", "PAID"):
        raise HTTPException(status_code=400, detail="Negotiation has already been finalized and paid.")
        
    # Check expiry
    if negotiation.expires_at and datetime.utcnow() > negotiation.expires_at:
        negotiation.status = "EXPIRED"
        db.commit()
        raise HTTPException(status_code=400, detail="This negotiation offer has expired.")
        
    result = merchant_agent.process_buyer_turn(
        db=db,
        negotiation=negotiation,
        buyer_message_text=payload.message,
        counter_price=payload.counter_price
    )
    
    return result

@router.get("/{negotiation_id}")
def get_negotiation_details(negotiation_id: str, db: Session = Depends(get_db)):
    n = db.query(Negotiation).filter(Negotiation.id == negotiation_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Negotiation not found")
        
    messages = db.query(NegotiationMessage).filter(
        NegotiationMessage.negotiation_id == negotiation_id
    ).order_by(NegotiationMessage.timestamp.asc()).all()
    
    offers = db.query(Offer).filter(
        Offer.id == n.active_offer_id
    ).first() if n.active_offer_id else None
    
    candidates = db.query(OfferCandidate).filter(
        OfferCandidate.negotiation_id == negotiation_id,
        OfferCandidate.round_number == n.current_round
    ).all()
    
    order = db.query(Order).filter(Order.negotiation_id == negotiation_id).first()
    p = n.product
    
    return {
        "id": n.id,
        "status": n.status,
        "current_round": n.current_round,
        "max_rounds": n.max_rounds,
        "buyer_query": n.buyer_initial_query,
        "buyer_budget": n.buyer_budget,
        "buyer": {
            "id": n.buyer.id,
            "name": n.buyer.name,
            "email": n.buyer.email,
            "is_agent": n.buyer.is_agent
        } if n.buyer else None,
        "product": {
            "id": p.id,
            "title": p.title,
            "brand": p.brand,
            "category": p.category,
            "base_price": p.base_price,
            "cost_price": p.cost_price,
            "shipping_cost": p.shipping_cost,
            "image_url": p.image_url,
            "thumbnail_url": p.thumbnail_url,
            "rating": p.rating or 4.5,
            "external_id": p.external_id,
            "specs": p.specs,
            "available_stock": (p.inventory.quantity - p.inventory.reserved_quantity) if p.inventory else 0,
            "inventory_age": p.inventory.age_days if p.inventory else 0
        } if p else None,
        "active_offer": {
            "id": offers.id,
            "round_number": offers.round_number,
            "list_price": offers.list_price,
            "offer_price": offers.offer_price,
            "discount_pct": offers.discount_pct,
            "discount_amount": offers.discount_amount,
            "free_shipping": offers.free_shipping,
            "warranty_months": offers.warranty_months,
            "bundle_items": offers.bundle_items,
            "merchant_cost": offers.merchant_cost,
            "merchant_margin": offers.merchant_margin,
            "p_conversion": offers.p_conversion,
            "expected_profit": offers.expected_profit,
            "bandit_action": offers.bandit_action,
            "status": offers.status,
            "reason_code": offers.reason_code,
            "explanation": offers.explanation
        } if offers else None,
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "final_price": order.final_price,
            "status": order.status
        } if order else None,
        "messages": [
            {
                "id": m.id,
                "sender_role": m.sender_role,
                "message_text": m.message_text,
                "offer_id": m.offer_id,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ],
        "round_candidates": [
            {
                "strategy_name": c.strategy_name,
                "candidate_price": c.candidate_price,
                "discount_pct": c.discount_pct,
                "free_shipping": c.free_shipping,
                "warranty_months": c.warranty_months,
                "calculated_margin": c.calculated_margin,
                "p_conversion": c.p_conversion,
                "expected_profit": c.expected_profit,
                "is_permissible": c.is_permissible,
                "policy_reason_code": c.policy_reason_code,
                "is_selected": c.is_selected
            }
            for c in candidates
        ]
    }
