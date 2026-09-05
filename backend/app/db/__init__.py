from sqlalchemy import text
from app.db.session import Base, engine, SessionLocal, get_db
from app.db.models import (
    User, Merchant, MerchantPolicy, Product, ProductEmbedding, Inventory,
    Buyer, BuyerPreference, Negotiation, NegotiationMessage, Offer,
    OfferCandidate, PricingEvent, BanditEvent, Order, Payment,
    PaymentEvent, AuditLog, ModelPrediction
)

def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info(products)"))
            cols = [row[1] for row in res.fetchall()]
            if cols:
                if "image_url" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)"))
                if "thumbnail_url" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN thumbnail_url VARCHAR(500)"))
                if "rating" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN rating FLOAT DEFAULT 4.5"))
                if "external_id" not in cols:
                    conn.execute(text("ALTER TABLE products ADD COLUMN external_id VARCHAR(100)"))
                conn.commit()
    except Exception as e:
        print(f"[init_db] Migration notice: {e}")
