"""
Real-World Product Ingestion & Live Fetching Service.
Connects to live e-commerce APIs (DummyJSON & Open E-Commerce standards)
to retrieve real-world products, specifications, media, ratings, and stock,
mapping them into the merchant inventory and deterministic policy engine.
"""

import re
import random
import requests
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.models import Product, Inventory, Merchant

DUMMYJSON_BASE_URL = "https://dummyjson.com/products"
USD_TO_INR_RATE = 85.0

# Target categories to focus on high-utility tech and consumer goods
TARGET_CATEGORIES = [
    "laptops",
    "smartphones",
    "tablets",
    "mobile-accessories",
    "sports-accessories",
    "mens-watches",
    "sunglasses"
]


def fetch_external_products(limit: int = 100, skip: int = 0, category: Optional[str] = None, timeout: int = 8) -> List[Dict[str, Any]]:
    """
    Fetches real-world products from DummyJSON API.
    """
    try:
        if category and category != "all":
            url = f"{DUMMYJSON_BASE_URL}/category/{category}"
            params = {"limit": limit, "skip": skip}
        else:
            url = DUMMYJSON_BASE_URL
            params = {"limit": limit, "skip": skip}
            
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("products", [])
    except Exception as e:
        print(f"[RealWorldProducts] Error fetching external products: {e}")
        return []


def search_external_products(query: str, limit: int = 10, timeout: int = 8) -> List[Dict[str, Any]]:
    """
    Performs real-time live search against external product catalog.
    """
    try:
        url = f"{DUMMYJSON_BASE_URL}/search"
        resp = requests.get(url, params={"q": query, "limit": limit}, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("products", [])
    except Exception as e:
        print(f"[RealWorldProducts] Error searching external products: {e}")
        return []


def extract_tech_specs(raw: Dict[str, Any], category: str) -> Dict[str, Any]:
    """
    Extracts hardware specs from real-world product title and description.
    """
    text = f"{raw.get('title', '')} {raw.get('description', '')}".lower()
    
    # 1. RAM extraction
    ram = None
    ram_match = re.search(r'(\d+)\s*(?:gb|gig)\s*(?:ram|memory)?', text)
    if ram_match:
        val = int(ram_match.group(1))
        if val in (4, 6, 8, 12, 16, 24, 32, 64):
            ram = val
    if not ram:
        if category == "laptops":
            ram = 32 if any(w in text for w in ["pro", "gaming", "studio", "max", "ultra"]) else 16
        elif category in ("smartphones", "tablets"):
            ram = 8 if any(w in text for w in ["pro", "ultra", "plus"]) else 6
        else:
            ram = 8

    # 2. Storage extraction
    storage = None
    tb_match = re.search(r'(\d+)\s*(?:tb|terabyte)\s*(?:ssd|storage|nvme|drive)?', text)
    if tb_match:
        storage = int(tb_match.group(1)) * 1000
    else:
        gb_match = re.search(r'(\d{2,4})\s*(?:gb)\s*(?:ssd|storage|nvme|drive|rom)?', text)
        if gb_match:
            val = int(gb_match.group(1))
            if val in (64, 128, 256, 512, 1000, 2000):
                storage = val
    if not storage:
        if category == "laptops":
            storage = 1000 if ram >= 32 else 512
        elif category in ("smartphones", "tablets"):
            storage = 256
        else:
            storage = 128

    # 3. Processor & Display heuristics
    processor = "High-efficiency Octa-Core Processor"
    if "intel" in text or "core" in text or "i7" in text or "i9" in text:
        processor = "Intel Core i7 / i9 High Performance"
    elif "ryzen" in text or "amd" in text:
        processor = "AMD Ryzen 7 Series"
    elif "apple" in text or "m1" in text or "m2" in text or "m3" in text:
        processor = "Apple M-Series Silicon"
    elif category == "smartphones":
        processor = "Snapdragon / Bionic Flagship Chip"

    display = "15.6-inch Full HD Display"
    if "oled" in text:
        display = "16-inch 3K OLED Display"
    elif "144hz" in text or "165hz" in text or "gaming" in text:
        display = "16-inch WQXGA 165Hz Fast Response"
    elif "retina" in text or "macbook" in text:
        display = "Liquid Retina High-Density Display"
    elif category == "smartphones":
        display = "6.7-inch 120Hz AMOLED Screen"

    return {
        "ram_gb": ram,
        "storage_gb": storage,
        "processor": processor,
        "display": display,
        "warranty": raw.get("warrantyInformation", "1 Year Comprehensive Warranty"),
        "shipping": raw.get("shippingInformation", "Ships in 2-3 business days"),
        "return_policy": raw.get("returnPolicy", "30 days merchant return policy"),
        "weight": raw.get("weight"),
        "dimensions": raw.get("dimensions"),
        "sku": raw.get("sku"),
        "tags": raw.get("tags", [])
    }


def transform_external_to_product(raw: Dict[str, Any], merchant_id: str) -> Dict[str, Any]:
    """
    Transforms external product payload into internal Product and Inventory schema.
    Converts USD to realistic INR pricing with sustainable 20-25% merchant margins.
    """
    cat_raw = raw.get("category", "laptops").lower()
    
    if "laptop" in cat_raw:
        category = "laptops"
    elif "phone" in cat_raw or "smart" in cat_raw:
        category = "smartphones"
    elif "tablet" in cat_raw:
        category = "tablets"
    elif "watch" in cat_raw:
        category = "watches"
    elif "audio" in cat_raw or "headphone" in cat_raw:
        category = "audio"
    else:
        category = cat_raw

    usd_price = float(raw.get("price", 99.99))
    inr_price = usd_price * USD_TO_INR_RATE
    
    if category == "laptops" and inr_price < 45000:
        inr_price = max(inr_price * 2.5, 54999.0)
    elif category == "smartphones" and inr_price < 15000:
        inr_price = max(inr_price * 2.0, 24999.0)
    
    base_price = round(inr_price, -1)
    cost_price = round(base_price * 0.78, 2)
    shipping_cost = 500.0 if base_price > 20000 else 200.0

    specs = extract_tech_specs(raw, category)
    
    raw_stock = int(raw.get("stock", 15))
    stock_qty = max(raw_stock, 3)
    
    images = raw.get("images", [])
    image_url = images[0] if images else raw.get("thumbnail")
    thumbnail_url = raw.get("thumbnail") or image_url

    return {
        "external_id": f"dummyjson_{raw.get('id')}",
        "merchant_id": merchant_id,
        "title": raw.get("title"),
        "brand": raw.get("brand") or "Premier Brand",
        "category": category,
        "description": raw.get("description"),
        "specs": specs,
        "base_price": base_price,
        "cost_price": cost_price,
        "shipping_cost": shipping_cost,
        "rating": float(raw.get("rating", 4.5)),
        "image_url": image_url,
        "thumbnail_url": thumbnail_url,
        "inventory": {
            "quantity": stock_qty,
            "reserved_quantity": 0,
            "age_days": random.randint(8, 45),
            "warehouse_location": random.choice(["BLR-WH-01", "BOM-WH-02", "DEL-WH-03"])
        }
    }


def upsert_real_world_product(db: Session, raw: Dict[str, Any], merchant_id: str) -> Product:
    """
    Inserts or updates a real-world product in the database.
    """
    transformed = transform_external_to_product(raw, merchant_id)
    ext_id = transformed["external_id"]
    
    existing = db.query(Product).filter(
        (Product.external_id == ext_id) | (Product.title == transformed["title"])
    ).first()

    if existing:
        existing.external_id = ext_id
        existing.base_price = transformed["base_price"]
        existing.cost_price = transformed["cost_price"]
        existing.rating = transformed["rating"]
        existing.image_url = transformed["image_url"]
        existing.thumbnail_url = transformed["thumbnail_url"]
        existing.specs = transformed["specs"]
        existing.is_active = True
        
        if existing.inventory:
            existing.inventory.quantity = max(existing.inventory.quantity, transformed["inventory"]["quantity"])
        else:
            inv = Inventory(
                product_id=existing.id,
                quantity=transformed["inventory"]["quantity"],
                reserved_quantity=0,
                age_days=transformed["inventory"]["age_days"],
                warehouse_location=transformed["inventory"]["warehouse_location"]
            )
            db.add(inv)
            
        db.commit()
        db.refresh(existing)
        return existing
    else:
        p = Product(
            external_id=ext_id,
            merchant_id=merchant_id,
            title=transformed["title"],
            brand=transformed["brand"],
            category=transformed["category"],
            description=transformed["description"],
            specs=transformed["specs"],
            base_price=transformed["base_price"],
            cost_price=transformed["cost_price"],
            shipping_cost=transformed["shipping_cost"],
            rating=transformed["rating"],
            image_url=transformed["image_url"],
            thumbnail_url=transformed["thumbnail_url"],
            is_active=True
        )
        db.add(p)
        db.commit()
        db.refresh(p)

        inv = Inventory(
            product_id=p.id,
            quantity=transformed["inventory"]["quantity"],
            reserved_quantity=0,
            age_days=transformed["inventory"]["age_days"],
            warehouse_location=transformed["inventory"]["warehouse_location"]
        )
        db.add(inv)
        db.commit()
        db.refresh(p)
        return p


def sync_all_real_world_products(db: Session, merchant_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches real-world catalog across target categories and syncs into merchant database.
    """
    merchants = db.query(Merchant).all()
    if not merchants:
        return {"status": "error", "message": "No merchants exist in database"}
        
    m1 = merchants[0]
    m2 = merchants[1] if len(merchants) > 1 else m1
    
    total_imported = 0
    total_updated = 0
    
    all_raw_products = []
    seen_ids = set()
    
    for cat in TARGET_CATEGORIES:
        prods = fetch_external_products(limit=30, category=cat)
        for p in prods:
            if p.get("id") not in seen_ids:
                seen_ids.add(p.get("id"))
                all_raw_products.append(p)
                
    general_prods = fetch_external_products(limit=60, skip=0)
    for p in general_prods:
        if p.get("id") not in seen_ids:
            seen_ids.add(p.get("id"))
            all_raw_products.append(p)

    for item in all_raw_products:
        assigned_merchant_id = merchant_id or (m1.id if random.random() < 0.6 else m2.id)
        
        ext_id = f"dummyjson_{item.get('id')}"
        existing = db.query(Product).filter(
            (Product.external_id == ext_id) | (Product.title == item.get("title"))
        ).first()
        
        upsert_real_world_product(db, item, assigned_merchant_id)
        if existing:
            total_updated += 1
        else:
            total_imported += 1
            
    return {
        "status": "success",
        "total_fetched": len(all_raw_products),
        "imported": total_imported,
        "updated": total_updated
    }
