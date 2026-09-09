import pandas as pd
from typing import List, Dict, Any, Optional
from app.config import CLEANED_CSV_PATH
from app.ml_model import churn_engine

class CSVDataLoader:
    """Loader and manager for historical CSV user records."""

    _cached_users: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def load_csv_users(cls, limit: int = 500) -> List[Dict[str, Any]]:
        """Load and cache CSV users enriched with ML churn predictions and churn reasons."""
        if cls._cached_users is not None:
            return cls._cached_users[:limit]

        if not CLEANED_CSV_PATH.exists():
            print(f"⚠️ Cleaned CSV dataset not found at {CLEANED_CSV_PATH}")
            return []

        try:
            df = pd.read_csv(CLEANED_CSV_PATH)
            users = []

            for _, row in df.iterrows():
                row_dict = row.to_dict()
                customer_id = int(row_dict.get("CustomerID", 0))
                email = f"customer{customer_id}@example.com"
                name = f"Customer {customer_id}"

                # Run ML model inference
                churn_pred, churn_prob, risk_level, churn_reasons = churn_engine.predict(row_dict)

                user_item = {
                    "id": f"csv-{customer_id}",
                    "source": "csv",
                    "customer_id": customer_id,
                    "email_or_name": f"{name} ({email})",
                    "email": email,
                    "full_name": name,
                    "tenure": float(row_dict.get("Tenure", 0)),
                    "complain": int(row_dict.get("Complain", 0)),
                    "satisfaction_score": int(row_dict.get("SatisfactionScore", 3)),
                    "city_tier": int(row_dict.get("CityTier", 1)),
                    "warehouse_to_home": float(row_dict.get("WarehouseToHome", 0)),
                    "preferred_payment_mode": str(row_dict.get("PreferredPaymentMode", "")),
                    "gender": str(row_dict.get("Gender", "")),
                    "prefered_order_cat": str(row_dict.get("PreferedOrderCat", "")),
                    "marital_status": str(row_dict.get("MaritalStatus", "")),
                    "churn_predicted": churn_pred,
                    "churn_probability": churn_prob,
                    "risk_level": risk_level,
                    "churn_reasons": churn_reasons,
                    "assigned_offers": churn_engine.suggest_offers(churn_reasons, risk_level) if churn_pred == 1 else []
                }
                users.append(user_item)

            cls._cached_users = users
            print(f"✅ Successfully loaded & processed {len(users)} CSV users with ML churn scores.")
            return cls._cached_users[:limit]

        except Exception as e:
            print(f"⚠️ Error loading CSV users: {e}")
            return []

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Find single CSV user by ID (e.g. 'csv-50001')."""
        all_users = cls.load_csv_users(limit=10000)
        for u in all_users:
            if u["id"] == user_id:
                return u
        return None
