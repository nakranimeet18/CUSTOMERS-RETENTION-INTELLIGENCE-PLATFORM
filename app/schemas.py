from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


# Customer Profile Base Schema
class CustomerProfileBase(BaseModel):
    tenure: float = Field(default=1.0, ge=0, description="Tenure in months")
    preferred_login_device: str = Field(default="Mobile Phone", description="Preferred login device")
    city_tier: int = Field(default=1, ge=1, le=3, description="City tier (1, 2, or 3)")
    warehouse_to_home: float = Field(default=10.0, ge=0, description="Distance from warehouse to home in km")
    preferred_payment_mode: str = Field(default="Credit Card", description="Payment mode preference")
    gender: str = Field(default="Female", description="Customer gender")
    hour_spend_on_app: float = Field(default=3.0, ge=0, description="Hours spent on mobile app")
    number_of_device_registered: int = Field(default=3, ge=1, description="Number of registered devices")
    prefered_order_cat: str = Field(default="Laptop & Accessory", description="Preferred order category")
    satisfaction_score: int = Field(default=3, ge=1, le=5, description="Satisfaction rating (1 to 5)")
    marital_status: str = Field(default="Single", description="Marital status")
    number_of_address: int = Field(default=2, ge=1, description="Number of registered shipping addresses")
    complain: int = Field(default=0, ge=0, le=1, description="Has customer complained (0=No, 1=Yes)")
    order_amount_hike_from_last_year: float = Field(default=15.0, description="Order amount hike percentage")
    coupon_used: float = Field(default=1.0, ge=0, description="Coupons used")
    order_count: float = Field(default=2.0, ge=0, description="Total order count")
    day_since_last_order: float = Field(default=5.0, ge=0, description="Days since last order")
    cashback_amount: float = Field(default=150.0, ge=0, description="Cashback amount earned")


class CustomerProfileCreate(CustomerProfileBase):
    pass


class CustomerProfileResponse(CustomerProfileBase):
    id: int
    user_id: int
    churn_predicted: int
    churn_probability: float
    risk_level: str
    churn_reasons: Optional[List[str]] = []

    model_config = ConfigDict(from_attributes=True)


# User Registration & Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Valid email address (e.g. user@gmail.com)")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: Optional[str] = Field(default=None, description="Full name")
    role: Optional[str] = Field(default="user", description="Role: 'user' or 'admin'")
    profile: Optional[CustomerProfileCreate] = Field(default=None, description="Initial customer profile attributes")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> str:
        if v:
            v_clean = v.strip().lower()
            if v_clean not in ["user", "admin"]:
                raise ValueError("Role must be either 'user' or 'admin'")
            return v_clean
        return "user"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User login email")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    created_at: datetime
    profile: Optional[CustomerProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Offer Schemas
class OfferCreate(BaseModel):
    title: str = Field(..., min_length=3, description="Offer title")
    description: str = Field(..., min_length=5, description="Offer description")
    discount_percentage: float = Field(default=10.0, ge=0.0, le=100.0, description="Discount percentage (0-100%)")
    voucher_code: Optional[str] = Field(default=None, description="Voucher coupon code")
    target_risk: str = Field(default="All", description="Target risk level: 'High', 'Medium', or 'All'")
    is_active: bool = Field(default=True, description="Active offer status")


class OfferResponse(OfferCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignOfferRequest(BaseModel):
    user_id: int = Field(..., ge=1, description="Target database user ID")
    offer_id: int = Field(..., ge=1, description="Target offer ID")
    notes: Optional[str] = Field(default=None, description="Optional assignment notes")


class UserOfferResponse(BaseModel):
    id: int
    user_id: int
    offer_id: int
    assigned_at: datetime
    status: str
    notes: Optional[str] = None
    offer: OfferResponse

    model_config = ConfigDict(from_attributes=True)


# Churn Prediction & Reason Response
class PredictionRequest(CustomerProfileBase):
    pass


class PredictionResponse(BaseModel):
    churn_predicted: int
    churn_probability: float
    risk_level: str
    churn_reasons: List[str]
    suggested_offers: List[str]


# Unified User Response (DB User + CSV User for Admin Panel)
class UnifiedUser(BaseModel):
    id: str  # Can be 'db-1' or 'csv-101'
    source: str  # 'database' or 'csv'
    email_or_name: str
    customer_id: Optional[int] = None
    tenure: float
    complain: int
    satisfaction_score: int
    churn_predicted: int
    churn_probability: float
    risk_level: str
    churn_reasons: List[str]
    assigned_offers: List[str] = []


# Admin Stats
class AdminDashboardStats(BaseModel):
    total_users: int
    churned_users: int
    retained_users: int
    churn_rate_percentage: float
    high_risk_count: int
    medium_risk_count: int
    active_offers_count: int
