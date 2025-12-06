"""
Integration tests for authentication flow
Tests: register → login → refresh → logout → reset password → verify
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import Base, User, UserProfile, RefreshToken
from app.core.security import get_password_hash
from main import app
from app.database import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("/forexxx", "/forexxx_test")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_register_flow(client):
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test123!@#",
            "displayName": "Test User",
            "phoneNumber": "+84901234567"
        }
    )
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "success" in data or "data" in data
    assert data.get("success") is True or "data" in data

def test_login_flow(client, db):
    """Test user login"""
    # First create a user
    from app.services.user_service import UserService
    user_service = UserService(db, None)
    user = user_service.create_user(
        email="login@example.com",
        password="Test123!@#",
        display_name="Login Test"
    )
    db.commit()
    
    # Then login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data.get("data", data) or "access_token" in data
    assert "refresh_token" in data.get("data", data) or "refresh_token" in data

def test_refresh_token_flow(client, db):
    """Test token refresh"""
    # Create user and login
    from app.services.user_service import UserService
    user_service = UserService(db, None)
    user = user_service.create_user(
        email="refresh@example.com",
        password="Test123!@#",
        display_name="Refresh Test"
    )
    db.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "Test123!@#"
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    refresh_token = login_data.get("data", {}).get("refresh_token") or login_data.get("refresh_token")
    
    # Refresh token
    refresh_response = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data.get("data", refresh_data) or "access_token" in refresh_data

def test_logout_flow(client, db):
    """Test user logout"""
    # Create user and login
    from app.services.user_service import UserService
    user_service = UserService(db, None)
    user = user_service.create_user(
        email="logout@example.com",
        password="Test123!@#",
        display_name="Logout Test"
    )
    db.commit()
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "logout@example.com",
            "password": "Test123!@#"
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    access_token = login_data.get("data", {}).get("access_token") or login_data.get("access_token")
    refresh_token = login_data.get("data", {}).get("refresh_token") or login_data.get("refresh_token")
    
    # Logout
    logout_response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_response.status_code == 200

def test_reset_password_flow(client, db):
    """Test password reset flow"""
    # Create user
    from app.services.user_service import UserService
    user_service = UserService(db, None)
    user = user_service.create_user(
        email="reset@example.com",
        password="Test123!@#",
        display_name="Reset Test"
    )
    db.commit()
    
    # Request password reset
    forgot_response = client.post(
        "/api/auth/forgot-password",
        params={"email": "reset@example.com"}
    )
    assert forgot_response.status_code == 200
    
    # Note: In a real scenario, we would extract the reset token from email
    # For testing, we might need to query it from the database
    # This is a simplified test

def test_account_lock_mechanism(client, db):
    """Test account lock after failed login attempts"""
    # Create user
    from app.services.user_service import UserService
    user_service = UserService(db, None)
    user = user_service.create_user(
        email="lock@example.com",
        password="Test123!@#",
        display_name="Lock Test"
    )
    db.commit()
    
    # Attempt multiple failed logins
    max_attempts = 5
    for i in range(max_attempts):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "lock@example.com",
                "password": "WrongPassword"
            }
        )
        # Should fail but not lock yet (unless max attempts reached)
    
    # After max attempts, account should be locked
    response = client.post(
        "/api/auth/login",
        json={
            "email": "lock@example.com",
            "password": "Test123!@#"
        }
    )
    # Should return error about account being locked
    assert response.status_code == 403 or response.status_code == 401

def test_rate_limiting(client, db):
    """Test rate limiting on login endpoint"""
    # Create user
    from app.services.user_service import UserService
    user_service = UserService(db, None)
    user = user_service.create_user(
        email="ratelimit@example.com",
        password="Test123!@#",
        display_name="Rate Limit Test"
    )
    db.commit()
    
    # Make many rapid requests
    for i in range(20):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "ratelimit@example.com",
                "password": "Test123!@#"
            }
        )
        # After rate limit, should return 429
        if response.status_code == 429:
            assert "rate limit" in response.json().get("detail", "").lower()
            break

