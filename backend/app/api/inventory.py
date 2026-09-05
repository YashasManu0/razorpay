from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import Inventory, Product, MerchantPolicy

router = APIRouter(prefix="/inventory", tags=["inventory"])

class InventoryUpdatePayload(BaseModel):
    quantity: Optional[int] = None
    age_days: Optional[int] = None
    warehouse_location: Optional[str] = None

@router.get("/")
def list_inventory(
    merchant_id: Optional[str] = None,
    filter_status: Optional[str] = None,  # all, low_stock, aging
    db: Session = Depends(get_db)
):
    q = db.query(Inventory).join(Product)
    if merchant_id:
        q = q.filter(Product.merchant_id == merchant_id)
        
    items = q.all()
    results = []
    for inv in items:
        p = inv.product
        available = inv.quantity - inv.reserved_quantity
        
        is_low_stock = available <= 5
        is_aging = inv.age_days >= 60
        
        if filter_status == "low_stock" and not is_low_stock:
            continue
        if filter_status == "aging" and not is_aging:
            continue
            
        status = "healthy"
        if available <= 0:
            status = "out_of_stock"
        elif is_low_stock:
            status = "low_stock"
        elif is_aging:
            status = "aging"
            
        results.append({
            "inventory_id": inv.id,
            "product_id": p.id,
            "product_title": p.title,
            "category": p.category,
            "brand": p.brand,
            "base_price": p.base_price,
            "quantity": inv.quantity,
            "reserved_quantity": inv.reserved_quantity,
            "available_stock": available,
            "age_days": inv.age_days,
            "warehouse_location": inv.warehouse_location,
            "status": status,
            "updated_at": inv.updated_at.isoformat() if inv.updated_at else None
        })
        
    return results

@router.patch("/{inventory_id}")
def update_inventory(inventory_id: str, payload: InventoryUpdatePayload, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
        
    if payload.quantity is not None:
        inv.quantity = max(0, payload.quantity)
    if payload.age_days is not None:
        inv.age_days = max(0, payload.age_days)
    if payload.warehouse_location:
        inv.warehouse_location = payload.warehouse_location
        
    db.commit()
    db.refresh(inv)
    return {
        "message": "Inventory updated successfully",
        "inventory_id": inv.id,
        "quantity": inv.quantity,
        "available_stock": inv.quantity - inv.reserved_quantity,
        "age_days": inv.age_days
    }
