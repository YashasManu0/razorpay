import pytest
from app.db.session import SessionLocal
from app.db.models import Product, Inventory, Merchant
from app.services.real_world_products import (
    transform_external_to_product,
    upsert_real_world_product,
    extract_tech_specs
)
from app.search.hybrid_search import HybridProductSearch


def test_extract_tech_specs_from_real_world_data():
    sample_raw = {
        "title": "MacBook Pro 16 M3 Max 32GB RAM 1TB SSD",
        "description": "Stunning Liquid Retina display with 32GB unified memory and 1TB ultra-fast SSD storage.",
        "category": "laptops",
        "warrantyInformation": "2 years official Apple warranty",
        "shippingInformation": "Ships overnight"
    }
    specs = extract_tech_specs(sample_raw, category="laptops")
    assert specs["ram_gb"] == 32
    assert specs["storage_gb"] == 1000
    assert "Apple" in specs["processor"] or "Silicon" in specs["processor"]
    assert specs["warranty"] == "2 years official Apple warranty"


def test_transform_external_to_product_economics():
    sample_raw = {
        "id": 9999,
        "title": "Ultra Performance Flagship Laptop",
        "brand": "TechCorp",
        "category": "laptops",
        "description": "High end laptop with 32GB RAM and 1000GB SSD",
        "price": 1200.0,  # USD
        "rating": 4.8,
        "stock": 18,
        "images": ["https://example.com/laptop1.webp"],
        "thumbnail": "https://example.com/thumb.webp"
    }
    merchant_id = "test_merchant_123"
    transformed = transform_external_to_product(sample_raw, merchant_id)

    assert transformed["external_id"] == "dummyjson_9999"
    assert transformed["base_price"] > 90000.0
    # Cost price must reflect ~78% of base price ensuring healthy margin
    expected_cost = round(transformed["base_price"] * 0.78, 2)
    assert transformed["cost_price"] == expected_cost
    assert transformed["rating"] == 4.8
    assert transformed["image_url"] == "https://example.com/laptop1.webp"
    assert transformed["thumbnail_url"] == "https://example.com/thumb.webp"
    assert transformed["inventory"]["quantity"] == 18


def test_upsert_real_world_product_in_db():
    db = SessionLocal()
    merchant = db.query(Merchant).first()
    assert merchant is not None

    # Clean up any leftover test record
    db.query(Product).filter(Product.external_id == "dummyjson_88888").delete()
    db.commit()

    raw_item = {
        "id": 88888,
        "title": "Live Real World Wireless Headset Pro",
        "brand": "SoundMaster",
        "category": "audio",
        "description": "Studio quality over-ear headphones with ANC",
        "price": 250.0,
        "rating": 4.7,
        "stock": 22,
        "images": ["https://example.com/sound1.webp"],
        "thumbnail": "https://example.com/sound_thumb.webp"
    }

    try:
        product = upsert_real_world_product(db, raw_item, merchant.id)
        assert product.id is not None
        assert product.external_id == "dummyjson_88888"
        assert product.title == "Live Real World Wireless Headset Pro"
        assert product.image_url == "https://example.com/sound1.webp"
        assert product.thumbnail_url == "https://example.com/sound_thumb.webp"
        assert product.rating == 4.7

        # Verify inventory was created
        inv = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        assert inv is not None
        assert inv.quantity == 22

        # Verify upsert idempotency / update
        raw_item["price"] = 280.0
        raw_item["stock"] = 30
        updated_product = upsert_real_world_product(db, raw_item, merchant.id)
        assert updated_product.id == product.id
        assert updated_product.inventory.quantity == 30
    finally:
        db.query(Product).filter(Product.external_id == "dummyjson_88888").delete()
        db.commit()
        db.close()
