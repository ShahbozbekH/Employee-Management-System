from fastapi.testclient import TestClient
from app.main import app

import pytest
import json
import os


def test_user_deletion_from_db(client):
    from app.model.employee_model import add_user, get_user_by_username, delete_user_by_username
    # Add a user
    user_data = {
        "username": "deleteuser",
        "email": "deleteuser@example.com",
        "full_name": "Delete User",
        "password": "deletepass",
        "role": "user"
    }
    add_user(user_data)
    # Ensure user exists
    user = get_user_by_username("deleteuser")
    assert user is not None
    # Delete user
    deleted = delete_user_by_username("deleteuser")
    assert deleted is True
    # Ensure user no longer exists
    user = get_user_by_username("deleteuser")
    assert user is None
def get_jwt_token_with_role(client, username, password, role="user"):
    # Register user if not exists
    # Use a strong password for all test users
    strong_password = "StrongPassw0rd!"
    reg_data = {
        "username": username,
        "email": f"{username}@example.com",
        "full_name": f"{username.title()} User",
        "password": strong_password,
        "role": role
    }
    client.post("/register", json=reg_data)
    response = client.post("/login", data={"username": username, "password": strong_password})
    assert response.status_code == 200
    return response.json()["access_token"]

# Test that only admin can add/delete employees
def test_add_employee_requires_admin(client):
    # Create a non-admin user
    user_token = get_jwt_token_with_role(client, "normaluser", "userpass", role="user")
    employee = {
        "employee_id": "E999",
        "name": "Unauthorized Add",
        "email": "unauth.add@example.com",
        "department": "IT",
        "position": "Intern",
        "status": "Active"
    }
    response = client.post("/employees/employee", json=employee, headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin privileges required"

def test_delete_employee_requires_admin(client):
    # Create a non-admin user
    user_token = get_jwt_token_with_role(client, "normaluser2", "userpass2", role="user")
    # Create an admin and add an employee
    admin_token = get_jwt_token_with_role(client, "adminuser", "adminpass", role="admin")
    employee = {
        "employee_id": "E998",
        "name": "To Be Deleted",
        "email": "delete.me@example.com",
        "department": "HR",
        "position": "HR Assistant",
        "status": "Active"
    }
    client.post("/employees/employee", json=employee, headers={"Authorization": f"Bearer {admin_token}"})
    # Try to delete as non-admin
    response = client.delete(f"/employees/{employee['employee_id']}", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin privileges required"

# JWT Auth Tests
def get_jwt_token(client):
    response = client.post("/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_login_success(client):
    response = client.post("/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(client):
    response = client.post("/login", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_employees_requires_jwt(client):
    response = client.get("/employees/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_employees_invalid_jwt(client):
    response = client.get("/employees/", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_employees_valid_jwt(client):
    token = get_jwt_token(client)
    response = client.get("/employees/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 404)

def test_health_no_auth_required(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "API is running"
# User registration test
def test_user_registration(client):
    from app.model.employee_model import delete_user_by_username
    # Ensure test user does not exist before registration
    delete_user_by_username("testuser")
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "StrongPassw0rd!"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert "id" in data or "_id" in data or "username" in data
    assert data["username"] == user_data["username"]

@pytest.fixture
def client():
    return TestClient(app)

# Load employee test cases from JSON
def load_employee_test_cases():
    json_path = os.path.join(os.path.dirname(__file__), "employee_test_cases.json")
    with open(json_path, "r") as f:
        return json.load(f)

employee_test_cases = load_employee_test_cases()

# Dynamic test for GET /employees endpoint


@pytest.mark.parametrize("employee", employee_test_cases)
def test_add_employee_dynamic(client, employee):
    token = get_jwt_token(client)
    response = client.post("/employees/employee", json=employee, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Employee added successfully"




@pytest.mark.parametrize("employee", employee_test_cases)
def test_get_employee_by_id_dynamic(client, employee):
    token = get_jwt_token(client)
    emp_id = employee["employee_id"]
    expected_name = employee["name"]
    # Ensure employee exists
    client.post("/employees/employee", json=employee, headers={"Authorization": f"Bearer {token}"})
    response = client.get(f"/employees/{emp_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == emp_id
    assert data["name"] == expected_name




@pytest.mark.parametrize("employee", employee_test_cases)
def test_update_employee_dynamic(client, employee):
    token = get_jwt_token(client)
    update_data = employee.copy()
    update_data["name"] = employee["name"] + " Updated"
    update_data["position"] = "Senior " + employee["position"]
    # Ensure employee exists
    client.post("/employees/employee", json=employee, headers={"Authorization": f"Bearer {token}"})
    response = client.put(f"/employees/employee/{update_data['employee_id']}", json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Employee updated successfully"




@pytest.mark.parametrize("employee", employee_test_cases)
def test_delete_employee_dynamic(client, employee):
    token = get_jwt_token(client)
    emp_id = employee["employee_id"]
    # Ensure employee exists before delete
    client.post("/employees/employee", json=employee, headers={"Authorization": f"Bearer {token}"})
    response = client.delete(f"/employees/{emp_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Employee deleted successfully"
    # Confirm deletion
    get_response = client.get(f"/employees/{emp_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_response.status_code == 404




@pytest.mark.parametrize("department", list(set(emp["department"] for emp in employee_test_cases)))
def test_get_employees_by_department_dynamic(client, department):
    token = get_jwt_token(client)
    # Ensure employees exist for the department
    dept_employees = [emp for emp in employee_test_cases if emp["department"] == department]
    for emp in dept_employees:
        client.post("/employees/employee", json=emp, headers={"Authorization": f"Bearer {token}"})
    response = client.get(f"/employees/department/{department}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for emp in dept_employees:
        assert any(e["id"] == emp["employee_id"] for e in data)
