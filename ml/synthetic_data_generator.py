"""
Synthetic Training Data Generator for Buyer Purchase Probability.
CLEAR LABEL: SYNTHETIC DEMO DATASET
Used for offline pre-training of the conversion probability model for hackathon demonstration.
"""

import numpy as np
import pandas as pd
from typing import Tuple

CATEGORIES = ["laptops", "smartphones", "monitors", "tablets", "audio", "accessories"]

def generate_synthetic_negotiation_dataset(n_samples: int = 15000, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    
    records = []
    
    for i in range(n_samples):
        category = np.random.choice(CATEGORIES, p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05])
        
        # Base prices depending on category
        if category == "laptops":
            base_price = np.random.uniform(45000, 150000)
        elif category == "smartphones":
            base_price = np.random.uniform(20000, 110000)
        elif category == "monitors":
            base_price = np.random.uniform(12000, 55000)
        elif category == "tablets":
            base_price = np.random.uniform(25000, 80000)
        elif category == "audio":
            base_price = np.random.uniform(5000, 30000)
        else:
            base_price = np.random.uniform(1500, 10000)
            
        base_price = round(base_price, -2)  # round to nearest 100
        
        # Buyer budget is distributed around base_price with some variance
        budget_ratio = np.random.normal(0.94, 0.08)  # average buyer wants 6% discount
        buyer_budget = round(base_price * budget_ratio, -2)
        
        # Candidate discount strategy
        discount_pct = np.random.choice([0.0, 2.0, 4.0, 6.0, 8.0, 10.0], p=[0.20, 0.20, 0.25, 0.20, 0.10, 0.05])
        offer_price = round(base_price * (1.0 - discount_pct / 100.0), 2)
        
        free_shipping = np.random.choice([True, False], p=[0.4, 0.6])
        warranty_months = np.random.choice([12, 24], p=[0.75, 0.25])
        
        budget_gap = offer_price - buyer_budget
        budget_gap_pct = (budget_gap / buyer_budget) * 100.0
        
        product_relevance = np.random.uniform(0.70, 0.99)
        inventory_quantity = np.random.randint(1, 40)
        inventory_age_days = np.random.randint(2, 90)
        delivery_days = np.random.randint(2, 7)
        urgency_score = np.random.uniform(0.2, 0.95)
        negotiation_round = np.random.choice([1, 2, 3], p=[0.45, 0.35, 0.20])
        previous_outcome = np.random.choice(["none", "converted", "abandoned"], p=[0.60, 0.25, 0.15])
        
        # Synthetic latent utility function (logistic behavior)
        # Higher discount, lower budget gap, higher relevance, faster delivery -> higher acceptance
        utility = 0.5
        utility += (discount_pct * 0.12)                         # +0.24 for 2%, +0.96 for 8%
        utility -= (budget_gap_pct * 0.15)                       # penalize if offer > budget
        utility += (product_relevance - 0.8) * 2.0               # relevance bonus
        utility += 0.35 if free_shipping else 0.0                # free shipping bump
        utility += 0.25 if warranty_months > 12 else 0.0         # warranty perk
        utility += (7 - delivery_days) * 0.06                    # fast delivery bonus
        utility += (negotiation_round - 1) * 0.20                # pressure to close in later rounds
        utility += (urgency_score - 0.5) * 0.60                  # high urgency buyers accept more readily
        
        if previous_outcome == "converted":
            utility += 0.25
        elif previous_outcome == "abandoned":
            utility -= 0.30
            
        # Sigmoid probability
        prob = 1.0 / (1.0 + np.exp(-utility))
        prob = np.clip(prob, 0.02, 0.98)
        
        # Realized acceptance binary outcome
        accepted = int(np.random.random() < prob)
        
        records.append({
            "category": category,
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
            "previous_outcome": previous_outcome,
            "free_shipping": int(free_shipping),
            "warranty_months": warranty_months,
            "true_probability": prob,
            "accepted": accepted
        })
        
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_synthetic_negotiation_dataset(5000)
    print("Generated synthetic dataset preview:")
    print(df.head())
    print(f"Overall synthetic acceptance rate: {df['accepted'].mean():.2%}")
