"""
Database Seed Script for AI Agent Negotiator.
Generates:
- 2 Merchants with realistic policies
- 105+ Products across 6 categories (Laptops, Smartphones, Monitors, Tablets, Audio, Accessories)
- Realistic inventory stock levels, ages (fresh to aging clearance), and warehouse locations
- 40+ Historical negotiations and orders for rich analytics
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Insert backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db.session import SessionLocal
from app.db import init_db
from app.db.models import (
    User, Merchant, MerchantPolicy, Product, Inventory, Buyer, BuyerPreference,
    Negotiation, NegotiationMessage, Offer, OfferCandidate, Order, Payment,
    PaymentEvent, AuditLog, BanditEvent
)

def seed():
    print("Initializing database tables...")
    init_db()
    db = SessionLocal()

    # Clear existing data
    print("Clearing previous seed data...")
    db.query(PaymentEvent).delete()
    db.query(Payment).delete()
    db.query(Order).delete()
    db.query(BanditEvent).delete()
    db.query(OfferCandidate).delete()
    db.query(Offer).delete()
    db.query(NegotiationMessage).delete()
    db.query(Negotiation).delete()
    db.query(BuyerPreference).delete()
    db.query(Buyer).delete()
    db.query(Inventory).delete()
    db.query(Product).delete()
    db.query(MerchantPolicy).delete()
    db.query(Merchant).delete()
    db.query(User).delete()
    db.query(AuditLog).delete()
    db.commit()

    print("Creating merchants and users...")
    user1 = User(email="admin@apextech.com", full_name="Vikram Sharma", role="merchant")
    user2 = User(email="admin@omnigear.com", full_name="Priya Patel", role="merchant")
    db.add_all([user1, user2])
    db.commit()

    merchant1 = Merchant(owner_id=user1.id, business_name="ApexTech Direct", currency="INR", status="active")
    merchant2 = Merchant(owner_id=user2.id, business_name="OmniGear Electronics", currency="INR", status="active")
    db.add_all([merchant1, merchant2])
    db.commit()

    policy1 = MerchantPolicy(
        merchant_id=merchant1.id,
        version=1,
        min_margin=5000.0,
        max_discount_pct=8.0,
        max_negotiation_rounds=3,
        low_stock_threshold=5,
        low_stock_max_discount=2.0,
        aging_threshold_days=60,
        aging_clearance_discount_boost=3.0,
        allow_free_shipping=True,
        allow_warranty_bundle=True,
        allow_accessory_bundle=True,
        min_delivery_days=2,
        max_delivery_days=6
    )

    policy2 = MerchantPolicy(
        merchant_id=merchant2.id,
        version=1,
        min_margin=3500.0,
        max_discount_pct=10.0,
        max_negotiation_rounds=4,
        low_stock_threshold=4,
        low_stock_max_discount=2.5,
        aging_threshold_days=50,
        aging_clearance_discount_boost=4.0,
        allow_free_shipping=True,
        allow_warranty_bundle=True,
        allow_accessory_bundle=True,
        min_delivery_days=1,
        max_delivery_days=5
    )
    db.add_all([policy1, policy2])
    db.commit()

    print("Seeding 105+ products...")

    # Laptop catalog definitions
    laptop_templates = [
        ("Lenovo Legion 5 Pro Gaming Laptop", "Lenovo", 78999.0, 62000.0, 32, 1000, "Ryzen 7 7745HX", "RTX 4060 8GB", "16-inch WQXGA 165Hz", 14, 18),
        ("Asus ROG Strix G16", "Asus", 84999.0, 68000.0, 32, 1000, "Core i7 13650HX", "RTX 4060 8GB", "16-inch FHD+ 165Hz", 4, 25),
        ("Acer Predator Helios Neo 16", "Acer", 76999.0, 61000.0, 16, 1000, "Core i7 13700HX", "RTX 4050 6GB", "16-inch WUXGA 165Hz", 18, 72),
        ("Dell Alienware m16 R2", "Dell", 149999.0, 122000.0, 32, 2000, "Intel Core Ultra 7", "RTX 4070 8GB", "16-inch QHD+ 240Hz", 8, 30),
        ("HP Omen 16 Gaming", "HP", 82999.0, 66000.0, 32, 1000, "Ryzen 7 7840HS", "RTX 4060 8GB", "16.1-inch FHD 165Hz", 3, 12),
        ("Apple MacBook Pro 16 M3 Pro", "Apple", 249900.0, 210000.0, 36, 1000, "Apple M3 Pro 12-core", "18-core GPU", "16.2-inch Liquid Retina XDR", 12, 15),
        ("Apple MacBook Air 15 M3", "Apple", 134900.0, 114000.0, 16, 512, "Apple M3 8-core", "10-core GPU", "15.3-inch Liquid Retina", 22, 10),
        ("Lenovo LOQ 15 Gaming", "Lenovo", 64999.0, 52000.0, 16, 512, "Core i5 13450HX", "RTX 3050 6GB", "15.6-inch FHD 144Hz", 28, 65),
        ("Asus TUF Gaming A15", "Asus", 69999.0, 56000.0, 16, 512, "Ryzen 7 7735HS", "RTX 4050 6GB", "15.6-inch FHD 144Hz", 6, 45),
        ("MSI Katana 17 B13V", "MSI", 89999.0, 72000.0, 32, 1000, "Core i7 13620H", "RTX 4060 8GB", "17.3-inch FHD 144Hz", 9, 80),
        ("HP Victus Gaming 16", "HP", 61999.0, 49000.0, 16, 512, "Ryzen 5 7640HS", "RTX 3050 6GB", "16.1-inch FHD 144Hz", 15, 22),
        ("Dell G15 5530 Gaming", "Dell", 73999.0, 59000.0, 16, 1000, "Core i7 13650HX", "RTX 3050 6GB", "15.6-inch FHD 120Hz", 11, 40),
        ("Asus ROG Zephyrus G14", "Asus", 139999.0, 115000.0, 32, 1000, "Ryzen 9 8945HS", "RTX 4070 8GB", "14-inch 3K OLED 120Hz", 5, 14),
        ("Lenovo ThinkPad P16s Gen 2", "Lenovo", 118999.0, 96000.0, 32, 1000, "Ryzen 7 PRO 7840U", "Radeon 780M", "16-inch WUXGA IPS", 8, 33),
        ("Acer Nitro 16 AMD", "Acer", 72999.0, 58000.0, 16, 512, "Ryzen 7 7735HS", "RTX 4050 6GB", "16-inch WUXGA 165Hz", 19, 75),
        ("Gigabyte AORUS 15", "Gigabyte", 98999.0, 79000.0, 32, 1000, "Core i7 13700H", "RTX 4070 8GB", "15.6-inch QHD 165Hz", 4, 62),
        ("Razer Blade 16", "Razer", 279999.0, 235000.0, 32, 2000, "Core i9 14900HX", "RTX 4080 12GB", "16-inch Dual-Mode Mini-LED", 3, 19),
        ("Samsung Galaxy Book4 Ultra", "Samsung", 189999.0, 155000.0, 32, 1000, "Core Ultra 7 155H", "RTX 4050 6GB", "16-inch 3K AMOLED 120Hz", 7, 28),
        ("LG Gram 17 SuperSlim", "LG", 112999.0, 91000.0, 16, 1000, "Core i7 1360P", "Intel Iris Xe", "17-inch WQXGA IPS", 12, 54),
        ("Dell XPS 15 9530", "Dell", 174999.0, 143000.0, 32, 1000, "Core i7 13700H", "RTX 4060 8GB", "15.6-inch 3.5K OLED Touch", 6, 21),
    ]

    # Additional procedural laptop variations
    for i in range(21, 46):
        brand = random.choice(["Lenovo", "Asus", "HP", "Dell", "Acer", "MSI"])
        ram = random.choice([16, 32, 64])
        ssd = random.choice([512, 1000, 2000])
        cost = random.randint(450, 1400) * 100
        price = round(cost * random.uniform(1.22, 1.35), -2)
        qty = random.randint(2, 35)
        age = random.randint(5, 85)
        title = f"{brand} MasterPro Studio {i} ({ram}GB / {ssd if ssd < 1000 else int(ssd/1000)}TB)"
        laptop_templates.append((
            title, brand, price, float(cost), ram, ssd,
            f"Core i{random.choice([5, 7, 9])} Gen 14",
            f"RTX {random.choice([4050, 4060, 4070])}",
            "16-inch QHD 165Hz", qty, age
        ))

    created_products = []

    for item in laptop_templates:
        title, brand, price, cost, ram, ssd, proc, gpu, disp, qty, age = item
        m_id = merchant1.id if random.random() < 0.65 else merchant2.id
        
        p = Product(
            merchant_id=m_id,
            title=title,
            brand=brand,
            category="laptops",
            description=f"High performance {brand} laptop with {ram}GB RAM, {ssd}GB NVMe SSD, {proc}, and {gpu}.",
            specs={
                "ram_gb": ram,
                "storage_gb": ssd,
                "processor": proc,
                "gpu": gpu,
                "display": disp
            },
            base_price=price,
            cost_price=cost,
            shipping_cost=500.0,
            image_url="https://cdn.dummyjson.com/product-images/laptops/lenovo-yoga-920/1.webp",
            thumbnail_url="https://cdn.dummyjson.com/product-images/laptops/lenovo-yoga-920/thumbnail.webp",
            rating=round(random.uniform(4.4, 4.9), 1),
            is_active=True
        )
        db.add(p)
        db.flush()

        inv = Inventory(
            product_id=p.id,
            quantity=qty,
            reserved_quantity=0,
            age_days=age,
            warehouse_location=random.choice(["BLR-WH-01", "BOM-WH-02", "DEL-WH-03"])
        )
        db.add(inv)
        created_products.append(p)

    # Smartphones
    smartphone_templates = [
        ("Apple iPhone 15 Pro Max", "Apple", 134900.0, 114000.0, {"ram_gb": 8, "storage_gb": 256, "chip": "A17 Pro", "display": "6.7 Super Retina XDR"}),
        ("Samsung Galaxy S24 Ultra", "Samsung", 129999.0, 108000.0, {"ram_gb": 12, "storage_gb": 512, "chip": "Snapdragon 8 Gen 3", "display": "6.8 Dynamic AMOLED 2X"}),
        ("OnePlus 12 5G", "OnePlus", 64999.0, 53000.0, {"ram_gb": 16, "storage_gb": 512, "chip": "Snapdragon 8 Gen 3", "display": "6.82 ProXDR 120Hz"}),
        ("Google Pixel 8 Pro", "Google", 93999.0, 78000.0, {"ram_gb": 12, "storage_gb": 256, "chip": "Google Tensor G3", "display": "6.7 Super Actua"}),
        ("Xiaomi 14 Ultra", "Xiaomi", 99999.0, 82000.0, {"ram_gb": 16, "storage_gb": 512, "chip": "Snapdragon 8 Gen 3", "display": "6.73 WQHD+ AMOLED"}),
    ]
    for i in range(6, 16):
        brand = random.choice(["Samsung", "OnePlus", "Google", "Vivo", "Realme"])
        cost = random.randint(180, 750) * 100
        price = round(cost * 1.25, -2)
        smartphone_templates.append((
            f"{brand} Neo Prime {i} 5G", brand, price, float(cost),
            {"ram_gb": random.choice([8, 12, 16]), "storage_gb": random.choice([128, 256, 512]), "chip": "Snapdragon 8 Series", "display": "6.7 AMOLED"}
        ))

    for item in smartphone_templates:
        title, brand, price, cost, specs = item
        p = Product(
            merchant_id=merchant2.id if random.random() < 0.6 else merchant1.id,
            title=title,
            brand=brand,
            category="smartphones",
            specs=specs,
            base_price=price,
            cost_price=cost,
            shipping_cost=300.0,
            image_url="https://cdn.dummyjson.com/product-images/smartphones/iphone-13-pro/1.webp",
            thumbnail_url="https://cdn.dummyjson.com/product-images/smartphones/iphone-13-pro/thumbnail.webp",
            rating=round(random.uniform(4.3, 4.8), 1),
            is_active=True
        )
        db.add(p)
        db.flush()
        inv = Inventory(product_id=p.id, quantity=random.randint(4, 40), reserved_quantity=0, age_days=random.randint(4, 70))
        db.add(inv)
        created_products.append(p)

    # Monitors
    monitor_brands = ["LG", "Samsung", "Dell", "BenQ", "Asus"]
    for i in range(1, 16):
        brand = random.choice(monitor_brands)
        cost = random.randint(140, 480) * 100
        price = round(cost * 1.28, -2)
        size = random.choice([27, 32, 34, 49])
        hz = random.choice([144, 165, 240, 360])
        p = Product(
            merchant_id=merchant1.id,
            title=f"{brand} UltraGear {size}-inch {hz}Hz QHD Monitor",
            brand=brand,
            category="monitors",
            specs={"screen_size": f"{size} inch", "refresh_rate": f"{hz}Hz", "resolution": "2560x1440 QHD", "panel": "Fast IPS"},
            base_price=price,
            cost_price=float(cost),
            shipping_cost=800.0,
            is_active=True
        )
        db.add(p)
        db.flush()
        inv = Inventory(product_id=p.id, quantity=random.randint(3, 20), reserved_quantity=0, age_days=random.randint(8, 75))
        db.add(inv)
        created_products.append(p)

    # Tablets & Audio
    for i in range(1, 13):
        cost = random.randint(200, 600) * 100
        p = Product(
            merchant_id=merchant2.id,
            title=f"Apple iPad Air Gen {i} 11-inch M2" if i <= 6 else f"Samsung Galaxy Tab S9 FE+{i}",
            brand="Apple" if i <= 6 else "Samsung",
            category="tablets",
            specs={"display": "11-inch Liquid Retina", "storage_gb": 128, "connectivity": "Wi-Fi + Cellular"},
            base_price=round(cost * 1.24, -2),
            cost_price=float(cost),
            shipping_cost=350.0,
            is_active=True
        )
        db.add(p)
        db.flush()
        inv = Inventory(product_id=p.id, quantity=random.randint(5, 25), reserved_quantity=0, age_days=random.randint(10, 60))
        db.add(inv)
        created_products.append(p)

    for i in range(1, 11):
        cost = random.randint(80, 240) * 100
        p = Product(
            merchant_id=merchant1.id,
            title=f"Sony WH-1000XM{i%5 + 1} Noise Cancelling Headphones" if i % 2 == 0 else f"Bose QuietComfort Ultra {i}",
            brand="Sony" if i % 2 == 0 else "Bose",
            category="audio",
            specs={"type": "Over-Ear Wireless", "anc": "Active Noise Cancelling", "battery": "30 Hours"},
            base_price=round(cost * 1.30, -2),
            cost_price=float(cost),
            shipping_cost=250.0,
            is_active=True
        )
        db.add(p)
        db.flush()
        inv = Inventory(product_id=p.id, quantity=random.randint(6, 30), reserved_quantity=0, age_days=random.randint(5, 45))
        db.add(inv)
        created_products.append(p)

    db.commit()
    print(f"Total base products created: {len(created_products)}")

    # Fetch and ingest real-world products from live e-commerce API (DummyJSON)
    print("Fetching and ingesting real-world products from live e-commerce API (DummyJSON)...")
    try:
        from app.services.real_world_products import sync_all_real_world_products
        sync_result = sync_all_real_world_products(db)
        print(f"Real-world products sync result: {sync_result}")
        # Refresh product list so historical negotiations and analytics encompass real products
        created_products = db.query(Product).all()
        print(f"Total active products in catalog: {len(created_products)}")
    except Exception as e:
        print(f"Notice: Offline fallback during real-world fetch ({e}). Proceeding with base catalog.")
    buyers = [
        Buyer(name="Siddharth Rao", email="siddharth.rao@techcorp.in", is_agent=True, risk_score=0.03),
        Buyer(name="Ananya Sharma", email="ananya.sharma@designhub.io", is_agent=True, risk_score=0.02),
        Buyer(name="Karan Verma", email="karan.v@freelance.net", is_agent=False, risk_score=0.05),
        Buyer(name="Shopping Agent Apex", email="buyer.agent.01@agentic.ai", is_agent=True, risk_score=0.01)
    ]
    db.add_all(buyers)
    db.commit()

    # Prepopulate historical negotiations and paid orders for rich analytics
    for i in range(45):
        buyer = random.choice(buyers)
        prod = random.choice(created_products[:25])
        
        # Decide if converted
        converted = random.random() < 0.44
        rounds = random.choice([1, 2, 3])
        
        discount_pct = random.choice([0.0, 2.0, 4.0, 6.0])
        offer_price = round(prod.base_price * (1.0 - discount_pct / 100.0), 2)
        margin = round(offer_price - prod.cost_price, 2)
        
        n = Negotiation(
            buyer_id=buyer.id,
            merchant_id=prod.merchant_id,
            product_id=prod.id,
            status="COMPLETED" if converted else "REJECTED",
            buyer_initial_query=f"I need a {prod.brand} {prod.category} under ₹{int(prod.base_price)}",
            buyer_budget=offer_price,
            current_round=rounds,
            max_rounds=3
        )
        db.add(n)
        db.flush()

        off = Offer(
            negotiation_id=n.id,
            product_id=prod.id,
            round_number=rounds,
            list_price=prod.base_price,
            offer_price=offer_price,
            discount_pct=discount_pct,
            discount_amount=prod.base_price - offer_price,
            merchant_cost=prod.cost_price,
            merchant_margin=margin,
            free_shipping=(random.random() < 0.3),
            warranty_months=12,
            p_conversion=0.65 if converted else 0.35,
            expected_profit=round(0.65 * margin, 2),
            bandit_action=random.choice(["FULL_PRICE", "DISCOUNT_2", "DISCOUNT_4", "FREE_SHIPPING", "WARRANTY"]),
            status="ACCEPTED" if converted else "REJECTED",
            reason_code="POLICY_PERMISSIBLE" if converted else "BUYER_DECLINED"
        )
        db.add(off)
        db.flush()
        n.active_offer_id = off.id

        if converted:
            ord_entry = Order(
                negotiation_id=n.id,
                merchant_id=prod.merchant_id,
                buyer_id=buyer.id,
                product_id=prod.id,
                offer_id=off.id,
                order_number=f"ORD-HIST-{i:04d}",
                final_price=offer_price,
                merchant_cost=prod.cost_price,
                realized_margin=margin,
                status="PAID"
            )
            db.add(ord_entry)
            db.flush()

            pay = Payment(
                order_id=ord_entry.id,
                provider="mock_razorpay",
                provider_order_id=f"order_hist_{i:04d}",
                provider_payment_id=f"pay_hist_{i:04d}",
                idempotency_key=f"idemp_hist_{i:04d}",
                verified_amount=offer_price,
                status="CAPTURED",
                is_signature_verified=True
            )
            db.add(pay)

        # Record bandit event
        be = BanditEvent(
            negotiation_id=n.id,
            context_vector=[0.95, 0.9, 0.5, 0.2, 0.7, rounds/3.0, 0.6],
            action_taken=off.bandit_action,
            predicted_reward=margin / 10000.0,
            actual_reward=(margin / 10000.0) if converted else 0.0,
            was_accepted=converted,
            realized_revenue=offer_price if converted else 0.0,
            realized_profit=margin if converted else 0.0
        )
        db.add(be)

    db.commit()
    print("Database seeding completed successfully!")
    print(f"Summary: 2 Merchants, {len(created_products)} Products, 45 Historical Negotiations & Orders.")

if __name__ == "__main__":
    seed()
