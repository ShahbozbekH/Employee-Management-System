
from app.model.employee_model import add_employee, get_all_employees, update_employee, get_employees_by_department, get_employee_by_id, delete_employee

def remove_employee(employee_id: str):
    deleted = delete_employee(employee_id)
    if deleted:
        return {"message": "Employee deleted successfully"}
    else:
        return {"message": "Employee not found"}
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse, Employee

#GET request handler for /employees endpoint
def fetch_all_employees():
    employees = get_all_employees()
    result = []
    for emp in employees:
        # Skip records missing required fields
        if not all([
            emp.get("employee_id"),
            emp.get("name"),
            emp.get("email"),
            emp.get("department")
        ]):
            continue
        created_at = emp.get("created_at")
        if not created_at:
            from datetime import datetime
            created_at = datetime.now()
        result.append(EmployeeResponse(
            id=emp["employee_id"],
            name=emp["name"],
            email=emp["email"],
            department=emp["department"],
            created_at=created_at
        ))
    return result

# GET employees by department
def fetch_employees_by_department(department: str):
    employees = get_employees_by_department(department)
    result = []
    for emp in employees:
        if not all([
            emp.get("employee_id"),
            emp.get("name"),
            emp.get("email"),
            emp.get("department")
        ]):
            continue
        created_at = emp.get("created_at")
        if not created_at:
            from datetime import datetime
            created_at = datetime.now()
        result.append(EmployeeResponse(
            id=emp["employee_id"],
            name=emp["name"],
            email=emp["email"],
            department=emp["department"],
            created_at=created_at
        ))
    return result

# GET employee by id
def fetch_employee_by_id(employee_id: str):
    emp = get_employee_by_id(employee_id)
    if emp and all([
        emp.get("employee_id"),
        emp.get("name"),
        emp.get("email"),
        emp.get("department")
    ]):
        created_at = emp.get("created_at")
        if not created_at:
            from datetime import datetime
            created_at = datetime.now()
        return EmployeeResponse(
            id=emp["employee_id"],
            name=emp["name"],
            email=emp["email"],
            department=emp["department"],
            created_at=created_at
        )
    return None

#POST/PUT request to add or update an employee

# Create employee
def create_employee_controller(employee_data):
    from datetime import datetime
    data = employee_data.model_dump()
    if not data.get("created_at"):
        data["created_at"] = datetime.now()
    add_employee(data)
    emp_resp = EmployeeResponse(
        id=data.get("employee_id"),
        name=data["name"],
        email=data["email"],
        department=data["department"],
        created_at=data["created_at"]
    )
    return {"message": "Employee added successfully", "employee": emp_resp}

# Update employee
def update_employee_controller(employee_id: str, employee_data):
    from datetime import datetime
    data = employee_data.model_dump()
    data["employee_id"] = employee_id
    if not data.get("created_at"):
        data["created_at"] = datetime.now()
    updated = update_employee(employee_id, data)
    if updated:
        emp_resp = EmployeeResponse(
            id=employee_id,
            name=data["name"],
            email=data["email"],
            department=data["department"],
            created_at=data["created_at"]
        )
        return {"message": "Employee updated successfully", "employee": emp_resp}
    else:
        return {"message": "Employee not found"}

