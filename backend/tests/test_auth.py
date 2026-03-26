from datetime import timedelta
import pytest
import pymongo
from app.config.database import users_collection
# Clear users collection before each test
@pytest.fixture(autouse=True)
def clear_users():
    users_collection.delete_many({})
    yield
from fastapi.testclient import TestClient
from app.main import app
import time

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "password": "StrongPassw0rd!",
        "role": "user",
        "email": "testuser@example.com",
        "full_name": "Test User"
    }

@pytest.fixture
def admin_data():
    return {
        "username": "adminuser",
        "password": "AdminPassw0rd!",
        "role": "admin",
        "email": "adminuser@example.com",
        "full_name": "Admin User"
    }

def register_user(client, user):
    return client.post("/register", json=user)

def login_user(client, username, password):
    return client.post("/login", data={"username": username, "password": password})

# --- TESTS ---
def test_register_user_success(client, user_data):
    response = register_user(client, user_data)
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"

def test_register_duplicate_username_returns_409(client, user_data):
    register_user(client, user_data)
    response = register_user(client, user_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"

def test_register_weak_password_returns_422(client, user_data):
    weak_user = user_data.copy()
    weak_user["password"] = "123"
    response = register_user(client, weak_user)
    assert response.status_code == 422
    detail = response.json()["detail"]
    if isinstance(detail, dict):
        assert "password" in detail
    elif isinstance(detail, list):
        # fallback for pydantic validation error
        assert any("password" in str(item) for item in detail)

def test_login_success_returns_jwt(client, user_data):
    register_user(client, user_data)
    response = login_user(client, user_data["username"], user_data["password"])
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password_returns_401(client, user_data):
    register_user(client, user_data)
    response = login_user(client, user_data["username"], "WrongPassword!")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_nonexistent_user_returns_401(client):
    response = login_user(client, "nouser", "anyPassword")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_protected_route_without_token_returns_401(client):
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_with_valid_token_succeeds(client, user_data):
    register_user(client, user_data)
    login_resp = login_user(client, user_data["username"], user_data["password"])
    token = login_resp.json()["access_token"]
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Access granted"

from app.utils.utils import create_access_token
def test_protected_route_with_expired_token_returns_401(client, user_data):
    register_user(client, user_data)
    # Create a token that expires immediately
    token = create_access_token({"sub": user_data["username"], "role": user_data["role"]}, expires_delta=timedelta(seconds=-1))
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired or invalid"

def test_admin_route_with_user_role_returns_403(client, user_data):
    register_user(client, user_data)
    login_resp = login_user(client, user_data["username"], user_data["password"])
    token = login_resp.json()["access_token"]
    response = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin privileges required"

# --- PASSWORD HASHING TESTS ---
def test_password_is_hashed_in_db_after_registration(client, user_data):
    """
    After registering a user, the password should not be stored in plain text in the database.
    The 'hashed_password' field should exist and not match the original password.
    """
    register_user(client, user_data)
    from app.model.employee_model import get_user_by_username
    db_user = get_user_by_username(user_data["username"])
    assert db_user is not None
    # The database should not have a 'password' field
    assert "password" not in db_user
    # The database should have a 'hashed_password' field
    assert "hashed_password" in db_user
    # The hashed password should not be the same as the plain password
    assert db_user["hashed_password"] != user_data["password"]
    # The hashed password should be a hex string of length 64 (sha256)
    assert isinstance(db_user["hashed_password"], str)
    assert len(db_user["hashed_password"]) == 64
