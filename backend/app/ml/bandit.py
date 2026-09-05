import os
import json
import numpy as np
from typing import List, Dict, Any, Optional

BANDIT_ACTIONS = [
    "FULL_PRICE",
    "DISCOUNT_2",
    "DISCOUNT_4",
    "DISCOUNT_6",
    "FREE_SHIPPING",
    "WARRANTY",
    "BUNDLE"
]

class LinUCBBandit:
    """
    Disjoint Linear Upper Confidence Bound (LinUCB) Contextual Bandit.
    Selects optimal permissible action to maximize Expected Profit while learning
    from realized conversion outcomes.
    """
    
    def __init__(self, d: int = 7, alpha: float = 1.0):
        self.d = d          # Context vector dimension
        self.alpha = alpha  # Exploration parameter
        self.actions = BANDIT_ACTIONS
        
        # A_a: d x d matrix for each action
        self.A = {a: np.identity(self.d) for a in self.actions}
        # b_a: d x 1 vector for each action
        self.b = {a: np.zeros((self.d, 1)) for a in self.actions}
        
        # Historical tracking for simulation & analytics
        self.history = []
        self.cumulative_profit = 0.0
        self.total_trials = 0
        
    def extract_context_vector(self, context: Dict[str, Any]) -> np.ndarray:
        """
        Extract normalized context vector of dimension d=7:
        1. buyer_budget / base_price (budget ratio)
        2. product_relevance (0.0 to 1.0)
        3. inventory scarcity (min(stock / 20.0, 1.0))
        4. inventory age ratio (min(age_days / 90.0, 1.0))
        5. urgency score (0.0 to 1.0)
        6. negotiation round ratio (round / 3.0)
        7. buyer discount sensitivity (0.0 to 1.0)
        """
        base_price = max(float(context.get("base_price", 80000.0)), 1.0)
        budget = float(context.get("buyer_budget", base_price * 0.95))
        budget_ratio = np.clip(budget / base_price, 0.5, 1.5)
        
        relevance = np.clip(float(context.get("product_relevance", 0.9)), 0.0, 1.0)
        stock = min(float(context.get("inventory_quantity", 10)) / 20.0, 1.0)
        age = min(float(context.get("inventory_age_days", 15)) / 90.0, 1.0)
        urgency = np.clip(float(context.get("urgency_score", 0.5)), 0.0, 1.0)
        round_ratio = float(context.get("negotiation_round", 1)) / 3.0
        sensitivity = np.clip(float(context.get("discount_sensitivity", 0.6)), 0.0, 1.0)
        
        x = np.array([budget_ratio, relevance, stock, age, urgency, round_ratio, sensitivity]).reshape(-1, 1)
        return x

    def select_action(
        self,
        context: Dict[str, Any],
        permissible_actions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Selects an action using LinUCB.
        IMPORTANT: Only selects from permissible_actions determined by the Policy Engine!
        """
        x = self.extract_context_vector(context)
        
        candidates = self.actions if permissible_actions is None else permissible_actions
        if not candidates:
            candidates = ["FULL_PRICE"]
            
        scores = {}
        for a in candidates:
            if a not in self.A:
                self.A[a] = np.identity(self.d)
                self.b[a] = np.zeros((self.d, 1))
                
            A_inv = np.linalg.inv(self.A[a])
            theta_hat = np.dot(A_inv, self.b[a])
            
            # LinUCB score: mean expected reward + exploration bonus
            mean = float(np.dot(theta_hat.T, x)[0, 0])
            variance = float(np.sqrt(np.dot(np.dot(x.T, A_inv), x))[0, 0])
            score = mean + self.alpha * variance
            scores[a] = score
            
        # Select action with highest UCB score
        best_action = max(scores, key=scores.get)
        
        return {
            "selected_action": best_action,
            "ucb_scores": {k: round(v, 4) for k, v in scores.items()},
            "context_vector": [round(float(v[0]), 3) for v in x],
            "permissible_actions": candidates
        }

    def update(self, action: str, context: Dict[str, Any], reward: float, profit: float, accepted: bool):
        """
        Update bandit parameters A and b using realized outcome.
        reward is typically normalized profit or utility.
        """
        if action not in self.A:
            self.A[action] = np.identity(self.d)
            self.b[action] = np.zeros((self.d, 1))
            
        x = self.extract_context_vector(context)
        self.A[action] += np.dot(x, x.T)
        self.b[action] += reward * x
        
        self.total_trials += 1
        self.cumulative_profit += profit if accepted else 0.0
        
        event = {
            "trial": self.total_trials,
            "action": action,
            "reward": round(reward, 4),
            "profit": round(profit, 2),
            "accepted": accepted,
            "cumulative_profit": round(self.cumulative_profit, 2)
        }
        self.history.append(event)
        if len(self.history) > 1000:
            self.history.pop(0)

# Global singleton bandit instance
bandit = LinUCBBandit(d=7, alpha=0.8)
