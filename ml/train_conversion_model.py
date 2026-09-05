"""
Train Purchase Probability Prediction Model on Synthetic Demo Dataset.
Saves model artifact to backend/app/ml/conversion_model.joblib
"""

import os
import sys
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, log_loss, brier_score_loss

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ml.synthetic_data_generator import generate_synthetic_negotiation_dataset

NUMERICAL_FEATURES = [
    "base_price",
    "offer_price",
    "discount_pct",
    "buyer_budget",
    "budget_gap",
    "budget_gap_pct",
    "product_relevance",
    "inventory_quantity",
    "inventory_age_days",
    "delivery_days",
    "urgency_score",
    "negotiation_round",
    "free_shipping",
    "warranty_months"
]

CATEGORICAL_FEATURES = ["category", "previous_outcome"]

def train_and_export_model(save_path: str = "backend/app/ml/conversion_model.joblib"):
    print("==================================================")
    print("TRAINING PURCHASE PROBABILITY MODEL (DEMO DATA)")
    print("==================================================")
    
    # 1. Generate synthetic dataset
    df = generate_synthetic_negotiation_dataset(n_samples=25000, random_seed=42)
    print(f"Generated {len(df)} synthetic negotiation records.")
    
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df["accepted"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 2. Build preprocessing transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
        ]
    )
    
    # 3. Model pipeline (Gradient Boosting with calibrated probability output)
    model = GradientBoostingClassifier(
        n_estimators=120,
        learning_rate=0.08,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", model)
    ])
    
    print("Fitting model pipeline...")
    pipeline.fit(X_train, y_train)
    
    # 4. Evaluation
    y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    loss = log_loss(y_test, y_pred_proba)
    brier = brier_score_loss(y_test, y_pred_proba)
    
    print("\n--- MODEL PERFORMANCE ON SYNTHETIC HOLDOUT ---")
    print(f"ROC-AUC Score : {auc:.4f}")
    print(f"Log Loss      : {loss:.4f}")
    print(f"Brier Score   : {brier:.4f}")
    print("NOTE: Trained on labeled synthetic demo data for hackathon simulation.")
    print("----------------------------------------------\n")
    
    # 5. Export package
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    export_payload = {
        "pipeline": pipeline,
        "features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES
        },
        "metadata": {
            "version": "1.0.0",
            "model_type": "GradientBoostingClassifier",
            "dataset_type": "SYNTHETIC_DEMO",
            "metrics": {
                "roc_auc": round(float(auc), 4),
                "log_loss": round(float(loss), 4),
                "brier_score": round(float(brier), 4)
            }
        }
    }
    
    joblib.dump(export_payload, save_path)
    print(f"Successfully saved trained model artifact to: {save_path}")

if __name__ == "__main__":
    train_and_export_model()
