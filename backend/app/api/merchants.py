from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.db.session import get_db
from app.db.models import Merchant, Product, Inventory, Negotiation, Order, MerchantPolicy

router = APIRouter(prefix="/merchants", tags=["merchants"])

@router.get("/")
def list_merchants(db: Session = Depends(get_db)):
    merchants = db.query(Merchant).all()
    res = []
    for m in merchants:
        product_count = db.query(Product).filter(Product.merchant_id == m.id).count()
        policy = db.query(MerchantPolicy).filter(MerchantPolicy.merchant_id == m.id, MerchantPolicy.is_active == True).first()
        res.append({
            "id": m.id,
            "business_name": m.business_name,
            "currency": m.currency,
            "status": m.status,
            "product_count": product_count,
            "policy": {
                "min_margin": policy.min_margin if policy else 4000.0,
                "max_discount_pct": policy.max_discount_pct if policy else 8.0,
                "max_rounds": policy.max_negotiation_rounds if policy else 3
            } if policy else None
        })
    return res

@router.get("/{merchant_id}/dashboard")
def get_merchant_dashboard(merchant_id: str, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
        
    total_products = db.query(Product).filter(Product.merchant_id == merchant_id).count()
    active_negotiations = db.query(Negotiation).filter(
        Negotiation.merchant_id == merchant_id,
        Negotiation.status.in_(["INITIATED", "PRODUCT_MATCHED", "OFFER_SENT", "COUNTER_RECEIVED", "FINAL_OFFER", "ACCEPTED", "PAYMENT_PENDING"])
    ).count()
    
    orders = db.query(Order).filter(Order.merchant_id == merchant_id).all()
    total_orders = len(orders)
    paid_orders = [o for o in orders if o.status in ("PAID", "CONFIRMED", "DELIVERED")]
    
    total_revenue = sum(o.final_price for o in paid_orders)
    total_profit = sum(o.realized_margin for o in paid_orders)
    avg_margin_pct = (total_profit / total_revenue * 100.0) if total_revenue > 0 else 22.5
    
    # Low stock and aging inventory alerts
    low_stock_products = db.query(Product).join(Inventory).filter(
        Product.merchant_id == merchant_id,
        (Inventory.quantity - Inventory.reserved_quantity) <= 5
    ).count()
    
    aging_products = db.query(Product).join(Inventory).filter(
        Product.merchant_id == merchant_id,
        Inventory.age_days >= 60
    ).count()
    
    return {
        "merchant": {
            "id": merchant.id,
            "business_name": merchant.business_name,
            "currency": merchant.currency
        },
        "kpis": {
            "total_products": total_products,
            "active_negotiations": active_negotiations,
            "total_orders": total_orders,
            "paid_orders": len(paid_orders),
            "conversion_rate": round(len(paid_orders) / max(total_orders, 1) * 100.0, 1),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "avg_margin_pct": round(avg_margin_pct, 1),
            "low_stock_alerts": low_stock_products,
            "aging_inventory_alerts": aging_products
        }
    }
