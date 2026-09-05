from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.session import get_db
from app.db.models import MerchantPolicy, Merchant, AuditLog

router = APIRouter(prefix="/policies", tags=["policies"])

class PolicyUpdatePayload(BaseModel):
    min_margin: Optional[float] = None
    max_discount_pct: Optional[float] = None
    max_negotiation_rounds: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    low_stock_max_discount: Optional[float] = None
    aging_threshold_days: Optional[int] = None
    aging_clearance_discount_boost: Optional[float] = None
    allow_free_shipping: Optional[bool] = None
    allow_warranty_bundle: Optional[bool] = None
    allow_accessory_bundle: Optional[bool] = None

@router.get("/")
def get_active_policy(merchant_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(MerchantPolicy).filter(MerchantPolicy.is_active == True)
    if merchant_id:
        q = q.filter(MerchantPolicy.merchant_id == merchant_id)
        
    policy = q.first()
    if not policy:
        # Create default policy if none exists
        first_merchant = db.query(Merchant).first()
        m_id = merchant_id or (first_merchant.id if first_merchant else "default_merchant")
        policy = MerchantPolicy(merchant_id=m_id)
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
    return {
        "id": policy.id,
        "merchant_id": policy.merchant_id,
        "version": policy.version,
        "min_margin": policy.min_margin,
        "max_discount_pct": policy.max_discount_pct,
        "max_negotiation_rounds": policy.max_negotiation_rounds,
        "low_stock_threshold": policy.low_stock_threshold,
        "low_stock_max_discount": policy.low_stock_max_discount,
        "aging_threshold_days": policy.aging_threshold_days,
        "aging_clearance_discount_boost": policy.aging_clearance_discount_boost,
        "allow_free_shipping": policy.allow_free_shipping,
        "allow_warranty_bundle": policy.allow_warranty_bundle,
        "allow_accessory_bundle": policy.allow_accessory_bundle,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None
    }

@router.patch("/{policy_id}")
def update_policy(policy_id: str, payload: PolicyUpdatePayload, db: Session = Depends(get_db)):
    policy = db.query(MerchantPolicy).filter(MerchantPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    changes = {}
    for k, v in payload.dict(exclude_unset=True).items():
        if v is not None:
            old_val = getattr(policy, k)
            setattr(policy, k, v)
            changes[k] = {"old": old_val, "new": v}
            
    policy.version += 1
    policy.updated_at = datetime.utcnow()
    
    # Audit log entry for policy update
    audit = AuditLog(
        entity_type="policy",
        entity_id=policy.id,
        action="UPDATE_MERCHANT_POLICY",
        actor="merchant_admin",
        details={
            "version": policy.version,
            "changes": changes
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(policy)
    
    return {
        "message": f"Policy updated to version {policy.version}",
        "policy": {
            "id": policy.id,
            "version": policy.version,
            "min_margin": policy.min_margin,
            "max_discount_pct": policy.max_discount_pct,
            "max_negotiation_rounds": policy.max_negotiation_rounds,
            "low_stock_threshold": policy.low_stock_threshold,
            "aging_threshold_days": policy.aging_threshold_days
        }
    }
