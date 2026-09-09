from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import User, CustomerProfile
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.ml_model import churn_engine

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user with email, password, and customer retention profile."""

    # Check if user email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # Create User account
    hashed_pwd = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name,
        role=user_data.role.lower() if user_data.role else "user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create CustomerProfile and run ML Churn Prediction
    profile_dict = user_data.profile.model_dump() if user_data.profile else {}
    
    # Run ML prediction engine
    churn_pred, churn_prob, risk_level, churn_reasons = churn_engine.predict(profile_dict)

    db_profile = CustomerProfile(
        user_id=db_user.id,
        tenure=profile_dict.get("tenure", 1.0),
        preferred_login_device=profile_dict.get("preferred_login_device", "Mobile Phone"),
        city_tier=profile_dict.get("city_tier", 1),
        warehouse_to_home=profile_dict.get("warehouse_to_home", 10.0),
        preferred_payment_mode=profile_dict.get("preferred_payment_mode", "Credit Card"),
        gender=profile_dict.get("gender", "Female"),
        hour_spend_on_app=profile_dict.get("hour_spend_on_app", 3.0),
        number_of_device_registered=profile_dict.get("number_of_device_registered", 3),
        prefered_order_cat=profile_dict.get("prefered_order_cat", "Laptop & Accessory"),
        satisfaction_score=profile_dict.get("satisfaction_score", 3),
        marital_status=profile_dict.get("marital_status", "Single"),
        number_of_address=profile_dict.get("number_of_address", 2),
        complain=profile_dict.get("complain", 0),
        order_amount_hike_from_last_year=profile_dict.get("order_amount_hike_from_last_year", 15.0),
        coupon_used=profile_dict.get("coupon_used", 1.0),
        order_count=profile_dict.get("order_count", 2.0),
        day_since_last_order=profile_dict.get("day_since_last_order", 5.0),
        cashback_amount=profile_dict.get("cashback_amount", 150.0),
        churn_predicted=churn_pred,
        churn_probability=churn_prob,
        risk_level=risk_level,
        churn_reasons=json.dumps(churn_reasons)
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_user)

    # Format churn_reasons list for response
    if db_user.profile and db_user.profile.churn_reasons:
        try:
            db_user.profile.churn_reasons = json.loads(db_user.profile.churn_reasons)
        except Exception:
            db_user.profile.churn_reasons = []

    return db_user


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with email and password, returning JWT access token."""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }


@router.post("/token", response_model=Token, summary="OAuth2 Authorize Token Endpoint (Swagger UI)")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token endpoint for Swagger UI Authorize modal."""
    return login(UserLogin(email=form_data.username, password=form_data.password), db)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return profile details of current logged in user."""
    if current_user.profile and current_user.profile.churn_reasons:
        try:
            if isinstance(current_user.profile.churn_reasons, str):
                current_user.profile.churn_reasons = json.loads(current_user.profile.churn_reasons)
        except Exception:
            current_user.profile.churn_reasons = []
    return current_user
