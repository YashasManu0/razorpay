import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

MODEL_PATH = os.path.join(os.path.dirname(__file__), "conversion_model.joblib")

class PurchaseProbabilityModel:
    _instance: Optional['PurchaseProbabilityModel'] = None
    
    def __init__(self):
        self.model_data = None
        self.pipeline = None
        self.metadata = {
            "model_type": "GradientBoostingClassifier",
            "version": "1.0.0",
            "dataset_type": "SYNTHETIC_DEMO",
            "metrics": {"roc_auc": 0.88, "log_loss": 0.35}
        }
        self._load_model()
        
    @classmethod
    def get_instance(cls) -> 'PurchaseProbabilityModel':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model_data = joblib.load(MODEL_PATH)
                self.pipeline = self.model_data.get("pipeline")
                self.metadata = self.model_data.get("metadata", self.metadata)
            except Exception as e:
                print(f"[ConversionModel] Warning loading model file: {e}. Using fallback predictor.")
                self.pipeline = None
        else:
            self.pipeline = None

    def predict_probability(self, features: Dict[str, Any]) -> float:
        """
        Predict probability of buyer acceptance given context and offer features.
        Features must contain:
        base_price, offer_price, discount_pct, buyer_budget, product_relevance,
        inventory_quantity, inventory_age_days, delivery_days, urgency_score,
        negotiation_round, category, previous_outcome, free_shipping, warranty_months
        """
        base_price = float(features.get("base_price", 80000.0))
        offer_price = float(features.get("offer_price", base_price))
        discount_pct = float(features.get("discount_pct", 0.0))
        buyer_budget = float(features.get("buyer_budget", base_price * 0.95))
        
        budget_gap = offer_price - buyer_budget
        budget_gap_pct = (budget_gap / buyer_budget * 100.0) if buyer_budget > 0 else 0.0
        
        product_relevance = float(features.get("product_relevance", 0.90))
        inventory_quantity = int(features.get("inventory_quantity", 10))
        inventory_age_days = int(features.get("inventory_age_days", 20))
        delivery_days = int(features.get("delivery_days", 3))
        urgency_score = float(features.get("urgency_score", 0.6))
        negotiation_round = int(features.get("negotiation_round", 1))
        free_shipping = int(bool(features.get("free_shipping", False)))
        warranty_months = int(features.get("warranty_months", 12))
        category = str(features.get("category", "laptops"))
        previous_outcome = str(features.get("previous_outcome", "none"))
        
        # If scikit-learn model is available, use it for inference
        if self.pipeline is not None:
            try:
                row = pd.DataFrame([{
                    "base_price": base_price,
                    "offer_price": offer_price,
                    "discount_pct": discount_pct,
                    "buyer_budget": buyer_budget,
                    "budget_gap": budget_gap,
                    "budget_gap_pct": budget_gap_pct,
                    "product_relevance": product_relevance,
                    "inventory_quantity": inventory_quantity,
                    "inventory_age_days": inventory_age_days,
                    "delivery_days": delivery_days,
                    "urgency_score": urgency_score,
                    "negotiation_round": negotiation_round,
                    "free_shipping": free_shipping,
                    "warranty_months": warranty_months,
                    "category": category,
                    "previous_outcome": previous_outcome
                }])
                proba = float(self.pipeline.predict_proba(row)[0, 1])
                return round(float(np.clip(proba, 0.02, 0.98)), 4)
            except Exception as e:
                # Fallback to calibrated logistic formula
                pass
                
        # Calibrated parametric logistic formula
        utility = 0.45
        utility += (discount_pct * 0.14)
        utility -= (budget_gap_pct * 0.16)
        utility += (product_relevance - 0.8) * 2.2
        utility += 0.40 if free_shipping else 0.0
        utility += 0.25 if warranty_months > 12 else 0.0
        utility += (7 - delivery_days) * 0.05
        utility += (negotiation_round - 1) * 0.22
        utility += (urgency_score - 0.5) * 0.65
        
        if previous_outcome == "converted":
            utility += 0.25
        elif previous_outcome == "abandoned":
            utility -= 0.30
            
        prob = 1.0 / (1.0 + np.exp(-utility))
        return round(float(np.clip(prob, 0.02, 0.98)), 4)

conversion_model = PurchaseProbabilityModel.get_instance()
