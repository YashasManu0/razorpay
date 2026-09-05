from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import Product, Inventory, MerchantPolicy
from app.search.hybrid_search import HybridProductSearch
from app.services.real_world_products import (
    sync_all_real_world_products, search_external_products, upsert_real_world_product
)

router = APIRouter(prefix="/products", tags=["products"])

class ProductUpdatePayload(BaseModel):
    base_price: Optional[float] = None
    cost_price: Optional[float] = None
    is_active: Optional[bool] = None

@router.get("/")
def list_products(
    category: Optional[str] = None,
    merchant_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    q = db.query(Product)
    if merchant_id:
        q = q.filter(Product.merchant_id == merchant_id)
    if category and category != "all":
        q = q.filter(Product.category == category)
    if search:
        q = q.filter(Product.title.ilike(f"%{search}%"))
        
    total = q.count()
    products = q.order_by(Product.base_price.desc()).offset(offset).limit(limit).all()
    
    items = []
    for p in products:
        inv = p.inventory
        margin = p.base_price - p.cost_price
        margin_pct = (margin / p.base_price * 100.0) if p.base_price > 0 else 0.0
        items.append({
            "id": p.id,
            "merchant_id": p.merchant_id,
            "external_id": p.external_id,
            "title": p.title,
            "brand": p.brand,
            "category": p.category,
            "description": p.description,
            "specs": p.specs or {},
            "base_price": p.base_price,
            "cost_price": p.cost_price,
            "shipping_cost": p.shipping_cost,
            "image_url": p.image_url,
            "thumbnail_url": p.thumbnail_url,
            "rating": p.rating or 4.5,
            "margin": round(margin, 2),
            "margin_pct": round(margin_pct, 1),
            "is_active": p.is_active,
            "inventory": {
                "quantity": inv.quantity if inv else 0,
                "reserved_quantity": inv.reserved_quantity if inv else 0,
                "available": (inv.quantity - inv.reserved_quantity) if inv else 0,
                "age_days": inv.age_days if inv else 0,
                "location": inv.warehouse_location if inv else "BLR-WH-01"
            } if inv else None
        })
        
    return {
        "total": total,
        "items": items
    }

@router.post("/sync-real-world")
def sync_real_world_catalog(merchant_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Triggers dynamic ingestion of real-world products from live e-commerce API (DummyJSON)
    into merchant catalog and inventory.
    """
    res = sync_all_real_world_products(db, merchant_id=merchant_id)
    return res

@router.get("/real-world/search")
def search_real_world_catalog(q: str = Query(..., description="Query for external live catalog")):
    """
    Live real-world product search from external e-commerce API.
    """
    results = search_external_products(query=q, limit=10)
    return {"query": q, "count": len(results), "items": results}

@router.get("/search")
def search_products(
    q: str = Query(..., description="Natural language search query"),
    merchant_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    results = HybridProductSearch.search(db, query=q, merchant_id=merchant_id, limit=5)
    output = []
    for r in results:
        p: Product = r["product"]
        inv: Inventory = r["inventory"]
        output.append({
            "id": p.id,
            "title": p.title,
            "brand": p.brand,
            "category": p.category,
            "specs": p.specs,
            "base_price": p.base_price,
            "cost_price": p.cost_price,
            "image_url": p.image_url,
            "thumbnail_url": p.thumbnail_url,
            "rating": p.rating or 4.5,
            "available_stock": r["available_stock"],
            "relevance_score": r["relevance_score"],
            "matched_constraints": r["matched_constraints"]
        })
    return output

@router.get("/{product_id}")
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
        
    inv = p.inventory
    margin = p.base_price - p.cost_price
    margin_pct = (margin / p.base_price * 100.0) if p.base_price > 0 else 0.0
    return {
        "id": p.id,
        "merchant_id": p.merchant_id,
        "external_id": p.external_id,
        "title": p.title,
        "brand": p.brand,
        "category": p.category,
        "description": p.description,
        "specs": p.specs,
        "base_price": p.base_price,
        "cost_price": p.cost_price,
        "shipping_cost": p.shipping_cost,
        "image_url": p.image_url,
        "thumbnail_url": p.thumbnail_url,
        "rating": p.rating or 4.5,
        "margin": round(margin, 2),
        "margin_pct": round(margin_pct, 1),
        "inventory": {
            "quantity": inv.quantity if inv else 0,
            "reserved": inv.reserved_quantity if inv else 0,
            "available": (inv.quantity - inv.reserved_quantity) if inv else 0,
            "age_days": inv.age_days if inv else 0
        } if inv else None
    }

@router.patch("/{product_id}")
def update_product(product_id: str, payload: ProductUpdatePayload, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if payload.base_price is not None:
        p.base_price = payload.base_price
    if payload.cost_price is not None:
        p.cost_price = payload.cost_price
    if payload.is_active is not None:
        p.is_active = payload.is_active
        
    db.commit()
    db.refresh(p)
    return {"message": "Product updated successfully", "id": p.id, "base_price": p.base_price}
