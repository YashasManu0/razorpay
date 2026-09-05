import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum, Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="merchant")  # merchant, admin, buyer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    merchants = relationship("Merchant", back_populates="owner")

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    business_name = Column(String(255), nullable=False, index=True)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="active")  # active, suspended
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="merchants")
    policies = relationship("MerchantPolicy", back_populates="merchant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="merchant", cascade="all, delete-orphan")
    negotiations = relationship("Negotiation", back_populates="merchant")
    orders = relationship("Order", back_populates="merchant")

class MerchantPolicy(Base):
    __tablename__ = "merchant_policies"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Financial and discount constraints
    min_margin = Column(Float, default=4000.0)             # Minimum allowed gross margin in INR
    max_discount_pct = Column(Float, default=8.0)          # Maximum permissible discount percentage (e.g. 8.0%)
    max_negotiation_rounds = Column(Integer, default=3)    # Maximum rounds before final offer
    
    # Inventory scarcity rules
    low_stock_threshold = Column(Integer, default=5)       # Threshold below which discounts are capped
    low_stock_max_discount = Column(Float, default=2.0)    # Capped discount when stock <= threshold
    aging_threshold_days = Column(Integer, default=60)     # Inventory age threshold for clearance eligibility
    aging_clearance_discount_boost = Column(Float, default=3.0) # Additional discount allowed for aged inventory
    
    # Incentive options
    allow_free_shipping = Column(Boolean, default=True)
    allow_warranty_bundle = Column(Boolean, default=True)
    allow_accessory_bundle = Column(Boolean, default=True)
    
    # Delivery constraints
    min_delivery_days = Column(Integer, default=2)
    max_delivery_days = Column(Integer, default=7)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="policies")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # laptops, smartphones, monitors, etc.
    description = Column(Text, nullable=True)
    
    # Hardware specifications JSON
    # { "ram_gb": 32, "storage_gb": 1000, "storage_type": "NVMe SSD", "processor": "Ryzen 7 7840HS", "gpu": "RTX 4060 8GB", "display": "16 inch 165Hz" }
    specs = Column(JSON, default=dict)
    
    # Financials
    base_price = Column(Float, nullable=False)   # Current listing price in INR
    cost_price = Column(Float, nullable=False)   # Unit merchant procurement cost in INR
    shipping_cost = Column(Float, default=500.0) # Standard delivery logistics cost in INR
    
    # Real-World Metadata & Media
    image_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    rating = Column(Float, default=4.5, nullable=True)
    external_id = Column(String(100), nullable=True, index=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    merchant = relationship("Merchant", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    embedding = relationship("ProductEmbedding", back_populates="product", uselist=False, cascade="all, delete-orphan")
    negotiations = relationship("Negotiation", back_populates="product")
    orders = relationship("Order", back_populates="product")

class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), unique=True, nullable=False)
    embedding_vector = Column(JSON, nullable=False)  # Normalized list of floats
    search_text = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="embedding")

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), unique=True, nullable=False)
    quantity = Column(Integer, default=10, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    age_days = Column(Integer, default=15, nullable=False)  # Days sitting in warehouse
    warehouse_location = Column(String(100), default="BLR-WH-01")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="inventory")

class Buyer(Base):
    __tablename__ = "buyers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_agent = Column(Boolean, default=False)  # True if AI shopping agent
    risk_score = Column(Float, default=0.05)   # 0.0 to 1.0 fraud/risk score
    created_at = Column(DateTime, default=datetime.utcnow)
    
    preferences = relationship("BuyerPreference", back_populates="buyer", uselist=False, cascade="all, delete-orphan")
    negotiations = relationship("Negotiation", back_populates="buyer")
    orders = relationship("Order", back_populates="buyer")

class BuyerPreference(Base):
    __tablename__ = "buyer_preferences"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    buyer_id = Column(String(36), ForeignKey("buyers.id"), unique=True, nullable=False)
    preferred_categories = Column(JSON, default=list)
    discount_sensitivity = Column(Float, default=0.7)  # 0.0 (price insensitive) to 1.0 (deal hunter)
    urgency_level = Column(Float, default=0.5)         # 0.0 (casual) to 1.0 (immediate purchase)
    historical_conversion_rate = Column(Float, default=0.65)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    buyer = relationship("Buyer", back_populates="preferences")

class Negotiation(Base):
    __tablename__ = "negotiations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    buyer_id = Column(String(36), ForeignKey("buyers.id"), nullable=False, index=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True, index=True)
    
    # State Machine:
    # INITIATED, PRODUCT_MATCHED, OFFER_GENERATED, OFFER_SENT, COUNTER_RECEIVED,
    # COUNTER_EVALUATED, FINAL_OFFER, ACCEPTED, PAYMENT_PENDING, PAID, COMPLETED,
    # REJECTED, EXPIRED, ESCALATED
    status = Column(String(50), default="INITIATED", nullable=False, index=True)
    
    buyer_initial_query = Column(Text, nullable=True)
    buyer_budget = Column(Float, nullable=True)
    buyer_max_delivery_days = Column(Integer, nullable=True)
    buyer_specs_extracted = Column(JSON, default=dict)
    
    current_round = Column(Integer, default=1)
    max_rounds = Column(Integer, default=3)
    active_offer_id = Column(String(36), nullable=True)
    
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    buyer = relationship("Buyer", back_populates="negotiations")
    merchant = relationship("Merchant", back_populates="negotiations")
    product = relationship("Product", back_populates="negotiations")
    messages = relationship("NegotiationMessage", back_populates="negotiation", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="negotiation", cascade="all, delete-orphan")
    candidates = relationship("OfferCandidate", back_populates="negotiation", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="negotiation")

class NegotiationMessage(Base):
    __tablename__ = "negotiation_messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=False, index=True)
    round_number = Column(Integer, default=1)
    sender_role = Column(String(50), nullable=False)  # buyer, merchant_ai, system
    message_text = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    offer_id = Column(String(36), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    negotiation = relationship("Negotiation", back_populates="messages")

class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    round_number = Column(Integer, default=1)
    
    # Financials determined strictly by pricing engine
    list_price = Column(Float, nullable=False)
    offer_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    discount_pct = Column(Float, default=0.0)
    merchant_cost = Column(Float, nullable=False)
    merchant_margin = Column(Float, nullable=False)
    
    # Inclusions & Perks
    free_shipping = Column(Boolean, default=False)
    warranty_months = Column(Integer, default=12)
    bundle_items = Column(JSON, default=list)  # [{"name": "Pro Gaming Mouse", "retail_val": 2499, "cost": 650}]
    delivery_days = Column(Integer, default=3)
    
    # Optimization Metrics
    p_conversion = Column(Float, default=0.5)
    expected_profit = Column(Float, default=0.0)
    bandit_action = Column(String(50), default="FULL_PRICE")
    
    # Status: DRAFT, PRESENTED, COUNTERED, ACCEPTED, REJECTED, EXPIRED
    status = Column(String(50), default="PRESENTED", nullable=False)
    reason_code = Column(String(100), default="OPTIMAL_EXPECTED_PROFIT")
    explanation = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    negotiation = relationship("Negotiation", back_populates="offers")

class OfferCandidate(Base):
    __tablename__ = "offer_candidates"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=False, index=True)
    round_number = Column(Integer, default=1)
    strategy_name = Column(String(100), nullable=False)  # FULL_PRICE, DISCOUNT_2, DISCOUNT_4, DISCOUNT_6, FREE_SHIPPING, etc.
    
    candidate_price = Column(Float, nullable=False)
    discount_pct = Column(Float, default=0.0)
    free_shipping = Column(Boolean, default=False)
    warranty_months = Column(Integer, default=12)
    bundle_name = Column(String(100), nullable=True)
    
    calculated_margin = Column(Float, nullable=False)
    p_conversion = Column(Float, nullable=False)
    expected_profit = Column(Float, nullable=False)
    
    is_permissible = Column(Boolean, default=True)
    policy_reason_code = Column(String(100), nullable=True)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    negotiation = relationship("Negotiation", back_populates="candidates")

class PricingEvent(Base):
    __tablename__ = "pricing_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # INITIAL_OFFER, COUNTER_EVALUATION, TIMEOUT_UPDATE
    input_context = Column(JSON, nullable=False)
    candidates_evaluated = Column(JSON, nullable=False)
    selected_offer_id = Column(String(36), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class BanditEvent(Base):
    __tablename__ = "bandit_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=False, index=True)
    context_vector = Column(JSON, nullable=False)
    action_taken = Column(String(50), nullable=False)
    predicted_reward = Column(Float, nullable=False)
    actual_reward = Column(Float, nullable=True)  # Populated when negotiation concludes
    was_accepted = Column(Boolean, nullable=True)
    realized_revenue = Column(Float, nullable=True)
    realized_profit = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=False, index=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("buyers.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    offer_id = Column(String(36), ForeignKey("offers.id"), nullable=False)
    
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    final_price = Column(Float, nullable=False)
    merchant_cost = Column(Float, nullable=False)
    realized_margin = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    
    shipping_address = Column(JSON, default=dict)
    delivery_status = Column(String(50), default="CONFIRMED")  # CONFIRMED, DISPATCHED, DELIVERED
    
    # Order state: CREATED, PAID, CANCELLED, REFUNDED
    status = Column(String(50), default="CREATED", nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    negotiation = relationship("Negotiation", back_populates="orders")
    merchant = relationship("Merchant", back_populates="orders")
    buyer = relationship("Buyer", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    provider = Column(String(50), default="razorpay")  # razorpay, mock
    
    provider_order_id = Column(String(100), nullable=True, index=True)
    provider_payment_id = Column(String(100), nullable=True, index=True)
    idempotency_key = Column(String(100), unique=True, nullable=False, index=True)
    
    # Server-verified amount (in paise or INR; stored here in INR float)
    verified_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    
    # PENDING, AUTHORIZED, CAPTURED, FAILED, REFUNDED
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    failure_reason = Column(String(255), nullable=True)
    
    signature = Column(String(255), nullable=True)
    is_signature_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order = relationship("Order", back_populates="payments")
    events = relationship("PaymentEvent", back_populates="payment", cascade="all, delete-orphan")

class PaymentEvent(Base):
    __tablename__ = "payment_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # payment.authorized, payment.captured, payment.failed
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)
    signature = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    processed_successfully = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    payment = relationship("Payment", back_populates="events")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False, index=True)  # negotiation, offer, payment, policy, security
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    actor = Column(String(50), default="system")  # buyer, merchant_ai, deterministic_engine, payment_gateway
    details = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=False, index=True)
    model_name = Column(String(100), default="conversion_gbm_v1")
    features = Column(JSON, nullable=False)
    prediction_score = Column(Float, nullable=False)  # Probability of conversion
    timestamp = Column(DateTime, default=datetime.utcnow)

# Indexes for fast lookup
Index("idx_product_cat_price", Product.category, Product.base_price)
Index("idx_inventory_qty_age", Inventory.quantity, Inventory.age_days)
Index("idx_negotiation_status", Negotiation.status, Negotiation.created_at)
