from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import Negotiation, Offer, Order, Payment, Inventory, AuditLog
from app.config import settings

class StateMachineError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

VALID_TRANSITIONS = {
    "INITIATED": ["PRODUCT_MATCHED", "REJECTED", "EXPIRED"],
    "PRODUCT_MATCHED": ["OFFER_GENERATED", "OFFER_SENT", "REJECTED", "EXPIRED"],
    "OFFER_GENERATED": ["OFFER_SENT", "REJECTED", "EXPIRED"],
    "OFFER_SENT": ["COUNTER_RECEIVED", "ACCEPTED", "REJECTED", "EXPIRED"],
    "COUNTER_RECEIVED": ["COUNTER_EVALUATED", "OFFER_SENT", "FINAL_OFFER", "REJECTED", "EXPIRED"],
    "COUNTER_EVALUATED": ["OFFER_SENT", "FINAL_OFFER", "ACCEPTED", "REJECTED", "EXPIRED", "ESCALATED"],
    "FINAL_OFFER": ["ACCEPTED", "REJECTED", "EXPIRED"],
    "ACCEPTED": ["PAYMENT_PENDING", "REJECTED", "EXPIRED"],
    "PAYMENT_PENDING": ["PAID", "FAILED", "EXPIRED"],
    "PAID": ["COMPLETED"],
    "COMPLETED": [],
    "REJECTED": [],
    "EXPIRED": [],
    "ESCALATED": []
}

class NegotiationStateMachine:
    """
    Authoritative State Machine for Negotiation and Payment Lifecycle.
    Enforces atomic transitions, inventory locks, and price integrity.
    """
    
    @staticmethod
    def transition(
        db: Session,
        negotiation: Negotiation,
        target_state: str,
        reason: str = "",
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Negotiation:
        current = negotiation.status
        allowed_next = VALID_TRANSITIONS.get(current, [])
        
        if target_state not in allowed_next:
            raise StateMachineError(
                code="INVALID_STATE_TRANSITION",
                message=f"Cannot transition negotiation from '{current}' to '{target_state}'. Allowed: {allowed_next}"
            )
            
        negotiation.status = target_state
        negotiation.updated_at = datetime.utcnow()
        
        # Log transition to Audit Trail
        log = AuditLog(
            entity_type="negotiation",
            entity_id=negotiation.id,
            action=f"TRANSITION_{current}_TO_{target_state}",
            actor=actor,
            details={
                "from_state": current,
                "to_state": target_state,
                "reason": reason,
                "metadata": metadata or {}
            }
        )
        db.add(log)
        db.commit()
        db.refresh(negotiation)
        return negotiation

    @staticmethod
    def reserve_inventory(db: Session, product_id: str) -> bool:
        """
        Atomically reserve 1 unit of stock for PAYMENT_PENDING state.
        Fails if available stock <= 0.
        """
        inv = db.query(Inventory).filter(Inventory.product_id == product_id).with_for_update().first()
        if not inv:
            return False
            
        available = inv.quantity - inv.reserved_quantity
        if available <= 0:
            return False
            
        inv.reserved_quantity += 1
        inv.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def release_inventory(db: Session, product_id: str):
        """Release reserved inventory upon payment failure or cancellation."""
        inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if inv and inv.reserved_quantity > 0:
            inv.reserved_quantity -= 1
            inv.updated_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def finalize_inventory_deduction(db: Session, product_id: str):
        """Permanently decrement inventory upon verified payment confirmation."""
        inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if inv:
            if inv.reserved_quantity > 0:
                inv.reserved_quantity -= 1
            if inv.quantity > 0:
                inv.quantity -= 1
            inv.updated_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def validate_payment_amount(
        db: Session,
        order_id: str,
        attempted_amount: float
    ) -> float:
        """
        Critical Financial Validation:
        Never trust client-side prices. Ensures payment amount matches the verified
        accepted offer stored in the database.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise StateMachineError("ORDER_NOT_FOUND", f"Order {order_id} does not exist.")
            
        # Compare amounts with small tolerance for float precision
        if abs(order.final_price - attempted_amount) > 0.01:
            raise StateMachineError(
                "PRICE_TAMPERING_DETECTED",
                f"Client attempted payment amount (₹{attempted_amount:,.2f}) does not match authorized order amount (₹{order.final_price:,.2f})."
            )
            
        return order.final_price
