import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

#test case for GET /employees endpoint 
def test_get_employees():
    # Ensure Jane Doe exists
    client.post("/employees/employee", json={
        "employee_id": "E002",
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "department": "Operations",
        "position": "Project Manager",
        "status": "Active"
    })
    response = client.get("/employees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(emp["name"] == "John Doe" for emp in response.json())
    assert any(emp["name"] == "Jane Doe" for emp in response.json())


def test_add_employee():
    new_employee = {
        "employee_id": "E002",
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "department": "Operations",
        "position": "Project Manager",
        "status": "Active"
    }
    response = client.post("/employees/employee", json=new_employee)
    assert response.status_code == 200
    assert response.json()["message"] == "Employee added successfully"

def test_update_employee():
    updated_employee = {
        "employee_id": "E002",
        "name": "Jane Doe Updated",
        "email": "jane.doe@example.com",
        "department": "Operations",
        "position": "Senior Project Manager",
        "status": "Active"
    }
    response = client.put("/employees/employee/E002", json=updated_employee)
    assert response.status_code == 200
    assert response.json()["message"] == "Employee updated successfully"




# Delete an employee test case /employees/{employee_id} endpoint
def test_delete_employee():
    # Ensure employee exists
    client.post("/employees/employee", json={
        "employee_id": "E006",
        "name": "Delete Me",
        "email": "deleteme@example.com",
        "department": "IT",
        "position": "SysAdmin",
        "status": "Active"
    })
    # Delete the employee
    response = client.delete("/employees/E006")
    assert response.status_code == 200
    assert response.json()["message"] == "Employee deleted successfully"
    # Confirm deletion
    get_response = client.get("/employees/E006")
    assert get_response.status_code == 404
#Delete an employee test case /employees/{employee_id} endpoint

# Get employee by ID test case /employees/{employee_id} endpoint
def test_get_employee_by_id():
    # Ensure employee exists
    client.post("/employees/employee", json={
        "employee_id": "E003",
        "name": "Alice Smith",
        "email": "alice.smith@example.com",
        "department": "HR",
        "position": "HR Manager",
        "status": "Active"
    })
    response = client.get("/employees/E003")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "E003"
    assert data["name"] == "Alice Smith"
    assert data["department"] == "HR"

# Get employees by department test case /employees/department/{department} endpoint
def test_get_employees_by_department():
    # Ensure employees exist
    client.post("/employees/employee", json={
        "employee_id": "E004",
        "name": "Bob Brown",
        "email": "bob.brown@example.com",
        "department": "Finance",
        "position": "Accountant",
        "status": "Active"
    })
    client.post("/employees/employee", json={
        "employee_id": "E005",
        "name": "Carol White",
        "email": "carol.white@example.com",
        "department": "Finance",
        "position": "CFO",
        "status": "Active"
    })
    response = client.get("/employees/department/Finance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(emp["id"] == "E004" for emp in data)
    assert any(emp["id"] == "E005" for emp in data)