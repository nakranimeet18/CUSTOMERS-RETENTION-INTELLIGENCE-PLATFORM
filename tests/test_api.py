import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.database import engine, Base

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def setup_and_teardown_db():
    """Reset database tables before running the test module."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test suite
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_root_health():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Customer Retention" in data["platform"]


def test_pydantic_validation_errors():
    """Verify that Pydantic schema validation correctly rejects malformed requests."""
    # 1. Invalid email format
    invalid_email_payload = {
        "email": "not-an-email",
        "password": "secretpassword123",
        "role": "user"
    }
    res = client.post("/api/auth/register", json=invalid_email_payload)
    assert res.status_code == 422  # Unprocessable Entity (Pydantic validation error)

    # 2. Invalid role (must be 'user' or 'admin')
    invalid_role_payload = {
        "email": "valid_user@example.com",
        "password": "secretpassword123",
        "role": "superhero"
    }
    res = client.post("/api/auth/register", json=invalid_role_payload)
    assert res.status_code == 422

    # 3. Satisfaction score out of range (must be between 1 and 5)
    invalid_score_payload = {
        "email": "valid_user2@example.com",
        "password": "secretpassword123",
        "profile": {
            "satisfaction_score": 10  # Exceeds max limit 5
        }
    }
    res = client.post("/api/auth/register", json=invalid_score_payload)
    assert res.status_code == 422


def test_user_registration_and_ml_prediction():
    user_payload = {
        "email": "testuser_churn_1@example.com",
        "password": "secretpassword123",
        "full_name": "Test Customer",
        "role": "USER ",  # Will be normalized by Pydantic field_validator
        "profile": {
            "tenure": 2.0,  # Low tenure -> potential churn trigger
            "preferred_login_device": "Mobile Phone",
            "city_tier": 1,
            "warehouse_to_home": 25.0,  # High warehouse distance
            "preferred_payment_mode": "Credit Card",
            "gender": "Female",
            "hour_spend_on_app": 3.0,
            "number_of_device_registered": 3,
            "prefered_order_cat": "Laptop & Accessory",
            "satisfaction_score": 1,  # Low satisfaction rating
            "marital_status": "Single",
            "number_of_address": 2,
            "complain": 1,  # Unresolved complaint -> strong churn trigger
            "order_amount_hike_from_last_year": 15.0,
            "coupon_used": 1.0,
            "order_count": 2.0,
            "day_since_last_order": 14.0,
            "cashback_amount": 100.0
        }
    }

    response = client.post("/api/auth/register", json=user_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser_churn_1@example.com"
    assert data["role"] == "user"
    assert data["profile"] is not None
    assert "churn_predicted" in data["profile"]
    assert "churn_probability" in data["profile"]
    assert len(data["profile"]["churn_reasons"]) > 0


def test_user_login():
    login_payload = {
        "email": "testuser_churn_1@example.com",
        "password": "secretpassword123"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_admin_flow_and_offer_assignment():
    # 1. Register Admin
    admin_payload = {
        "email": "admin_retention@example.com",
        "password": "adminsecretpassword",
        "full_name": "Platform Admin",
        "role": "admin"
    }
    client.post("/api/auth/register", json=admin_payload)

    # 2. Login Admin
    login_res = client.post("/api/auth/login", json={"email": "admin_retention@example.com", "password": "adminsecretpassword"})
    assert login_res.status_code == 200
    admin_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Get Admin Dashboard Stats
    stats_res = client.get("/api/admin/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_users"] > 0

    # 4. Get Unified Users (CSV + DB)
    users_res = client.get("/api/admin/users?limit=10", headers=headers)
    assert users_res.status_code == 200
    users_list = users_res.json()
    assert len(users_list) > 0

    # 5. Get Churned Users with Churn Reasons
    churned_res = client.get("/api/admin/churned-users", headers=headers)
    assert churned_res.status_code == 200
    churned_list = churned_res.json()
    assert len(churned_list) >= 0

    # 6. Create Retention Offer
    offer_payload = {
        "title": "Special VIP Apology Retention Pass",
        "description": "Exclusive 25% discount voucher for churn-risk customers.",
        "discount_percentage": 25.0,
        "voucher_code": "APOLOGY25",
        "target_risk": "High"
    }
    offer_res = client.post("/api/admin/offers", json=offer_payload, headers=headers)
    assert offer_res.status_code == 201
    offer_data = offer_res.json()
    offer_id = offer_data["id"]

    # 7. Assign Offer to Test User
    me_user_res = client.post("/api/auth/login", json={"email": "testuser_churn_1@example.com", "password": "secretpassword123"})
    user_id = me_user_res.json()["user_id"]
    user_token = me_user_res.json()["access_token"]

    assign_payload = {
        "user_id": user_id,
        "offer_id": offer_id,
        "notes": "Assigned via Admin Retention Panel"
    }
    assign_res = client.post("/api/admin/assign-offer", json=assign_payload, headers=headers)
    assert assign_res.status_code == 200

    # 8. User retrieves assigned offers
    user_offers_res = client.get("/api/users/offers", headers={"Authorization": f"Bearer {user_token}"})
    assert user_offers_res.status_code == 200
    user_offers = user_offers_res.json()
    assert len(user_offers) == 1
    assert user_offers[0]["offer"]["voucher_code"] == "APOLOGY25"
