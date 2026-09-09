from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from typing import List

from app.database import get_db
from app.models import User, CustomerProfile, UserOffer
from app.schemas import CustomerProfileResponse, CustomerProfileCreate, UserOfferResponse
from app.auth import get_current_user
from app.ml_model import churn_engine

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile", response_model=CustomerProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch customer retention profile for current user."""
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    if profile.churn_reasons and isinstance(profile.churn_reasons, str):
        try:
            profile.churn_reasons = json.loads(profile.churn_reasons)
        except Exception:
            profile.churn_reasons = []

    return profile


@router.put("/profile", response_model=CustomerProfileResponse)
def update_profile(
    profile_data: CustomerProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile parameters and re-run ML churn model prediction."""
    profile = current_user.profile
    if not profile:
        profile = CustomerProfile(user_id=current_user.id)
        db.add(profile)

    data_dict = profile_data.model_dump()
    for key, value in data_dict.items():
        setattr(profile, key, value)

    # Re-predict using ML model
    churn_pred, churn_prob, risk_level, churn_reasons = churn_engine.predict(data_dict)
    profile.churn_predicted = churn_pred
    profile.churn_probability = churn_prob
    profile.risk_level = risk_level
    profile.churn_reasons = json.dumps(churn_reasons)

    db.commit()
    db.refresh(profile)

    profile.churn_reasons = churn_reasons
    return profile


@router.get("/offers", response_model=List[UserOfferResponse])
def get_my_offers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve retention offers assigned to current user by Admin."""
    user_offers = db.query(UserOffer).filter(UserOffer.user_id == current_user.id).all()
    return user_offers
