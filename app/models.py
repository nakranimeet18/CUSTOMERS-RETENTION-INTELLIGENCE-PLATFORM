from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User account table (Users and Admins)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user", nullable=False)  # 'user' or 'admin'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("CustomerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    assigned_offers = relationship("UserOffer", back_populates="user", cascade="all, delete-orphan")


class CustomerProfile(Base):
    """Customer profile table storing retention attributes & ML predictions."""
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Customer numerical & categorical features
    tenure = Column(Float, default=1.0)
    preferred_login_device = Column(String(100), default="Mobile Phone")
    city_tier = Column(Integer, default=1)
    warehouse_to_home = Column(Float, default=10.0)
    preferred_payment_mode = Column(String(100), default="Credit Card")
    gender = Column(String(50), default="Female")
    hour_spend_on_app = Column(Float, default=3.0)
    number_of_device_registered = Column(Integer, default=3)
    prefered_order_cat = Column(String(100), default="Laptop & Accessory")
    satisfaction_score = Column(Integer, default=3)
    marital_status = Column(String(50), default="Single")
    number_of_address = Column(Integer, default=2)
    complain = Column(Integer, default=0)
    order_amount_hike_from_last_year = Column(Float, default=15.0)
    coupon_used = Column(Float, default=1.0)
    order_count = Column(Float, default=2.0)
    day_since_last_order = Column(Float, default=5.0)
    cashback_amount = Column(Float, default=150.0)

    # ML Predictions & Explainability
    churn_predicted = Column(Integer, default=0)
    churn_probability = Column(Float, default=0.0)
    risk_level = Column(String(50), default="Low")
    churn_reasons = Column(Text, nullable=True)  # JSON or comma-separated reasons
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class Offer(Base):
    """Retention offers created by admin."""
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    discount_percentage = Column(Float, default=10.0)
    voucher_code = Column(String(100), nullable=True)
    target_risk = Column(String(50), default="All")  # 'High', 'Medium', 'All'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_assignments = relationship("UserOffer", back_populates="offer", cascade="all, delete-orphan")


class UserOffer(Base):
    """Offers assigned to specific users."""
    __tablename__ = "user_offers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="assigned")  # 'assigned', 'redeemed', 'expired'
    notes = Column(String(255), nullable=True)

    user = relationship("User", back_populates="assigned_offers")
    offer = relationship("Offer", back_populates="user_assignments")
