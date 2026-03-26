
from fastapi import APIRouter, HTTPException, Depends
from app.controller.employee_controller import fetch_all_employees, create_employee_controller, update_employee_controller, fetch_employees_by_department, fetch_employee_by_id, remove_employee
from app.schemas.employee_schema import Employee, EmployeeCreate, EmployeeResponse, EmployeeMessageResponse
from app.utils.utils import require_admin
from datetime import datetime

router = APIRouter()

# Delete employee by id (admin only)
@router.delete("/{employee_id}", dependencies=[Depends(require_admin)])
def delete_employee_route(employee_id: str):
    result = remove_employee(employee_id)
    if result["message"] == "Employee deleted successfully":
        return result
    raise HTTPException(status_code=404, detail="Employee not found")


@router.get("/", response_model=list[EmployeeResponse])
def get_employees():
    return fetch_all_employees()

# Get employees by department
@router.get("/department/{department}", response_model=list[EmployeeResponse])
def get_employees_by_department_route(department: str):
    return fetch_employees_by_department(department)

# Get employee by id
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee_by_id_route(employee_id: str):
    emp = fetch_employee_by_id(employee_id)
    if emp:
        return emp
    raise HTTPException(status_code=404, detail="Employee not found")


# Add or update employee (POST for add, PUT for update)

# Add employee (POST, admin only)
@router.post("/employee", response_model=EmployeeMessageResponse, dependencies=[Depends(require_admin)])
def add_employee(employee: EmployeeCreate):
    return create_employee_controller(employee)

# Update employee (PUT)
@router.put("/employee/{employee_id}", response_model=EmployeeMessageResponse)
def update_employee_route(employee_id: str, employee: EmployeeCreate):
    result = update_employee_controller(employee_id, employee)
    if result["message"] == "Employee updated successfully":
        return result
    raise HTTPException(status_code=404, detail="Employee not found")