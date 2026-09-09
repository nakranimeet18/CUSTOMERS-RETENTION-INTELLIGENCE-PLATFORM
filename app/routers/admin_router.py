from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import json
from typing import List, Optional

from app.database import get_db
from app.models import User, CustomerProfile, Offer, UserOffer
from app.schemas import (
    OfferCreate, OfferResponse, AssignOfferRequest, UserOfferResponse,
    AdminDashboardStats, UnifiedUser
)
from app.auth import get_current_admin
from app.csv_loader import CSVDataLoader
from app.ml_model import churn_engine

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])


@router.get("/users", response_model=List[UnifiedUser])
def get_all_users(
    limit: int = Query(default=100, ge=1, le=1000),
    source: Optional[str] = Query(default=None, description="Filter by 'database', 'csv', or all"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Fetch all users across both historical CSV files and newly registered database accounts.
    Includes ML churn prediction, risk level, and churn reasons.
    """
    unified_list: List[UnifiedUser] = []

    # 1. Fetch DB Users
    if source in [None, "database"]:
        db_users = db.query(User).filter(User.role == "user").all()
        for u in db_users:
            profile = u.profile
            churn_reasons = []
            if profile and profile.churn_reasons:
                try:
                    churn_reasons = json.loads(profile.churn_reasons) if isinstance(profile.churn_reasons, str) else profile.churn_reasons
                except Exception:
                    churn_reasons = []

            # Get assigned offer titles
            assigned_offers = [uo.offer.title for uo in u.assigned_offers if uo.offer]

            item = UnifiedUser(
                id=f"db-{u.id}",
                source="database",
                email_or_name=f"{u.full_name or 'User'} ({u.email})",
                customer_id=u.id,
                tenure=profile.tenure if profile else 0.0,
                complain=profile.complain if profile else 0,
                satisfaction_score=profile.satisfaction_score if profile else 3,
                churn_predicted=profile.churn_predicted if profile else 0,
                churn_probability=profile.churn_probability if profile else 0.0,
                risk_level=profile.risk_level if profile else "Low",
                churn_reasons=churn_reasons,
                assigned_offers=assigned_offers
            )
            unified_list.append(item)

    # 2. Fetch CSV Users
    if source in [None, "csv"]:
        csv_users = CSVDataLoader.load_csv_users(limit=limit)
        for cu in csv_users:
            item = UnifiedUser(
                id=cu["id"],
                source="csv",
                email_or_name=cu["email_or_name"],
                customer_id=cu["customer_id"],
                tenure=cu["tenure"],
                complain=cu["complain"],
                satisfaction_score=cu["satisfaction_score"],
                churn_predicted=cu["churn_predicted"],
                churn_probability=cu["churn_probability"],
                risk_level=cu["risk_level"],
                churn_reasons=cu["churn_reasons"],
                assigned_offers=cu["assigned_offers"]
            )
            unified_list.append(item)

    return unified_list[:limit]


@router.get("/churned-users", response_model=List[UnifiedUser])
def get_churned_users(
    min_probability: float = Query(default=0.5, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Fetch all churned / high-risk users (from CSV and DB) with their churn probability
    and specific reasons WHY they churned.
    """
    all_users = get_all_users(limit=1000, source=None, db=db, admin=admin)
    churned = [u for u in all_users if u.churn_probability >= min_probability or u.churn_predicted == 1]
    return churned


@router.get("/stats", response_model=AdminDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Summary overview stats for Admin Dashboard."""
    all_users = get_all_users(limit=10000, source=None, db=db, admin=admin)

    total_users = len(all_users)
    churned = [u for u in all_users if u.churn_predicted == 1]
    retained = total_users - len(churned)
    churn_rate = (len(churned) / total_users * 100.0) if total_users > 0 else 0.0

    high_risk = len([u for u in all_users if u.risk_level == "High"])
    medium_risk = len([u for u in all_users if u.risk_level == "Medium"])

    active_offers = db.query(Offer).filter(Offer.is_active == True).count()

    return AdminDashboardStats(
        total_users=total_users,
        churned_users=len(churned),
        retained_users=retained,
        churn_rate_percentage=round(churn_rate, 2),
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        active_offers_count=active_offers
    )


@router.get("/offers", response_model=List[OfferResponse])
def get_offers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """List all retention offers in the platform."""
    offers = db.query(Offer).all()
    if not offers:
        # Seed default default offers if empty
        default_offers = [
            Offer(
                title="VIP Apology & Priority Support",
                description="24/7 Priority VIP support line + $15 instant refund credit for customer complaints.",
                discount_percentage=15.0,
                voucher_code="VIPCARE15",
                target_risk="High"
            ),
            Offer(
                title="Express Shipping Pass",
                description="Free express delivery pass on next 3 orders to eliminate shipping delays.",
                discount_percentage=10.0,
                voucher_code="EXPRESSFREE",
                target_risk="Medium"
            ),
            Offer(
                title="Loyalty Reactivation Discount",
                description="20% discount on order value for returning users inactive for over 10 days.",
                discount_percentage=20.0,
                voucher_code="LOYALTY20",
                target_risk="High"
            )
        ]
        db.add_all(default_offers)
        db.commit()
        offers = db.query(Offer).all()
    return offers


@router.post("/offers", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer_data: OfferCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Create a new retention offer in Admin Panel."""
    offer = Offer(**offer_data.model_dump())
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


@router.post("/assign-offer", response_model=UserOfferResponse)
def assign_offer_to_user(
    request: AssignOfferRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Assign a retention offer to a specific registered user."""
    target_user = db.query(User).filter(User.id == request.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found in database")

    target_offer = db.query(Offer).filter(Offer.id == request.offer_id).first()
    if not target_offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    user_offer = UserOffer(
        user_id=request.user_id,
        offer_id=request.offer_id,
        notes=request.notes or f"Assigned by Admin ({admin.email})"
    )
    db.add(user_offer)
    db.commit()
    db.refresh(user_offer)
    return user_offer
