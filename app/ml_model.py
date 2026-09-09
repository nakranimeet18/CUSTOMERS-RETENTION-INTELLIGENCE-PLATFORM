import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.config import MODEL_PATH, FEATURE_COLUMNS_PATH


class ChurnPredictionEngine:
    """ML Churn prediction and explainability engine for Customer Retention Platform."""

    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.load_model()

    def load_model(self):
        """Load pickled XGBoost classifier and feature columns list."""
        try:
            with open(FEATURE_COLUMNS_PATH, "rb") as f:
                self.feature_columns = pickle.load(f)
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            print(f"✅ Loaded ML Churn Model ({type(self.model).__name__}) with {len(self.feature_columns)} features.")
        except Exception as e:
            print(f"⚠️ Error loading ML model: {e}")
            self.model = None
            self.feature_columns = []

    def preprocess_input(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform raw user/customer profile dictionary into the exact 28 feature vector
        expected by the pre-trained XGBoost model.
        """
        # Create empty row dictionary with default zeros for all model columns
        row = {col: 0.0 for col in self.feature_columns}

        # Directly assign numerical features
        num_fields = [
            'OrderCount', 'NumberOfAddress', 'WarehouseToHome', 'CashbackAmount',
            'OrderAmountHikeFromlastYear', 'DaySinceLastOrder', 'CityTier',
            'Tenure', 'CouponUsed', 'HourSpendOnApp', 'NumberOfDeviceRegistered',
            'SatisfactionScore', 'Complain'
        ]

        for field in num_fields:
            # Handle camelCase / snake_case input keys flexibly
            snake_key = self._camel_to_snake(field)
            val = data.get(field, data.get(snake_key, 0))
            if field in row:
                row[field] = float(val) if val is not None else 0.0

        # Encode PreferredLoginDevice: Mobile Phone / Phone -> 1, Computer / Laptop -> 0
        device = str(data.get("preferred_login_device", data.get("PreferredLoginDevice", "Mobile Phone"))).lower()
        if "phone" in device or "mobile" in device:
            row["PreferredLoginDevice"] = 1.0
        else:
            row["PreferredLoginDevice"] = 0.0

        # Encode Gender: Male / M -> 1, Female / F -> 0
        gender = str(data.get("gender", data.get("Gender", "Female"))).lower()
        row["Gender"] = 1.0 if gender.startswith("m") else 0.0

        # One-hot encode PreferredPaymentMode
        payment = str(data.get("preferred_payment_mode", data.get("PreferredPaymentMode", "")))
        for mode in ['Cash on Delivery', 'Credit Card', 'Debit Card', 'E wallet', 'UPI']:
            col_name = f"PreferredPaymentMode_{mode}"
            if col_name in row:
                if mode.lower() in payment.lower():
                    row[col_name] = 1.0

        # One-hot encode PreferedOrderCat
        cat = str(data.get("prefered_order_cat", data.get("PreferedOrderCat", "")))
        for category in ['Fashion', 'Grocery', 'Laptop & Accessory', 'Mobile Phone', 'Others']:
            col_name = f"PreferedOrderCat_{category}"
            if col_name in row:
                if category.lower() in cat.lower():
                    row[col_name] = 1.0

        # One-hot encode MaritalStatus
        marital = str(data.get("marital_status", data.get("MaritalStatus", "")))
        for status in ['Divorced', 'Married', 'Single']:
            col_name = f"MaritalStatus_{status}"
            if col_name in row:
                if status.lower() == marital.lower():
                    row[col_name] = 1.0

        # Return single-row DataFrame with strict column order
        df = pd.DataFrame([row])[self.feature_columns]
        return df

    def predict(self, data: Dict[str, Any]) -> Tuple[int, float, str, List[str]]:
        """
        Run churn prediction and generate actionable churn reasons.
        Returns (churn_predicted, churn_probability, risk_level, churn_reasons).
        """
        if self.model is None:
            # Fallback if model not loaded
            return 0, 0.1, "Low", ["Model not initialized."]

        df_input = self.preprocess_input(data)

        # Get prediction and probabilities
        prob_churn = float(self.model.predict_proba(df_input)[0][1])
        predicted_class = int(prob_churn >= 0.5)

        # Risk Level Assessment
        if prob_churn >= 0.65:
            risk_level = "High"
        elif prob_churn >= 0.35:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Generate explainable churn reasons based on key feature risk thresholds
        reasons = self._generate_churn_reasons(data, prob_churn)

        return predicted_class, round(prob_churn, 4), risk_level, reasons

    def _generate_churn_reasons(self, data: Dict[str, Any], prob_churn: float) -> List[str]:
        """Examine customer feature values to output specific, human-readable churn drivers."""
        reasons = []

        complain = data.get("complain", data.get("Complain", 0))
        tenure = float(data.get("tenure", data.get("Tenure", 0)))
        satisfaction = float(data.get("satisfaction_score", data.get("SatisfactionScore", 3)))
        warehouse_dist = float(data.get("warehouse_to_home", data.get("WarehouseToHome", 0)))
        days_since_order = float(data.get("day_since_last_order", data.get("DaySinceLastOrder", 0)))
        cashback = float(data.get("cashback_amount", data.get("CashbackAmount", 0)))
        payment_mode = str(data.get("preferred_payment_mode", data.get("PreferredPaymentMode", "")))

        # Rule 1: Customer Complaints
        if int(complain) == 1:
            reasons.append("Customer filed an unresolved complaint (High impact on churn).")

        # Rule 2: Low Tenure
        if tenure <= 3.0:
            reasons.append(f"Low Tenure ({tenure} months) — new user at risk of early exit.")
        elif tenure <= 6.0:
            reasons.append(f"Moderate Tenure ({tenure} months) — user has not formed strong brand loyalty.")

        # Rule 3: Low Satisfaction Score
        if satisfaction <= 2.0:
            reasons.append(f"Low Satisfaction Rating ({satisfaction}/5).")

        # Rule 4: Long Shipping Distance
        if warehouse_dist >= 20.0:
            reasons.append(f"Long Warehouse Distance ({warehouse_dist} km) leading to potential delivery delays.")

        # Rule 5: High Inactivity Days
        if days_since_order >= 12.0:
            reasons.append(f"Inactivity detected ({days_since_order} days since last order).")

        # Rule 6: Low Cashback / Rewards
        if cashback < 120.0:
            reasons.append(f"Below-average cashback rewards earned (${cashback}).")

        # Rule 7: COD Payment Mode Risk
        if "cash on delivery" in payment_mode.lower() or "cod" in payment_mode.lower():
            reasons.append("Cash-on-Delivery payment preference correlates with lower engagement.")

        if not reasons:
            if prob_churn >= 0.5:
                reasons.append("Combined behavioral risk indicators suggest imminent churn risk.")
            else:
                reasons.append("Customer shows positive engagement metrics with low churn risk.")

        return reasons

    def suggest_offers(self, reasons: List[str], risk_level: str) -> List[str]:
        """Suggest personalized retention offers based on churn reasons."""
        offers = []

        reason_text = " ".join(reasons).lower()

        if "complaint" in reason_text:
            offers.append("🎟️ Priority 24/7 VIP Customer Support + $15 Service Apology Voucher")
        if "tenure" in reason_text or "new user" in reason_text:
            offers.append("🎁 20% Welcome-Back Discount Code (WELCOME20) for next purchase")
        if "satisfaction" in reason_text:
            offers.append("⭐ Free Premium Membership for 1 Month & Priority Feedback Call")
        if "warehouse" in reason_text or "delivery" in reason_text:
            offers.append("🚚 Free Express Shipping Pass on Next 3 Orders (EXPRESSFREE)")
        if "inactivity" in reason_text:
            offers.append("🔔 $10 Loyalty Credit bonus if order is placed within 48 hours")
        if "cashback" in reason_text:
            offers.append("💰 Double Cashback Points Promotion on all orders this month")

        if not offers:
            if risk_level == "High":
                offers.append("🔥 Exclusive 15% VIP Retention Coupon (VIP15)")
            else:
                offers.append("✨ Standard Loyalty Reward (5% Cashback on next purchase)")

        return list(set(offers))

    def _camel_to_snake(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Singleton instance
churn_engine = ChurnPredictionEngine()
