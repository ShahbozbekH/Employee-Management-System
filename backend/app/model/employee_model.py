# Delete user by username (for test purposes)
def delete_user_by_username(username: str):
    result = users_collection.delete_one({"username": username})
    return result.deleted_count > 0
# Delete employee by id
def delete_employee(employee_id: str):
    result = employees_collection.delete_one({"employee_id": employee_id})
    return result.deleted_count > 0
#Query the Database for Employee Data
from app.config.database import employees_collection
from app.schemas.employee_schema import Employee, EmployeeResponse

# Import users_collection for user operations
from app.config.database import users_collection
from app.schemas.employee_schema import User, UserCreate, UserResponse
from datetime import datetime
from bson import ObjectId

# Helper to hash password (simple placeholder, use a real hasher in production)
import hashlib
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Add user to users collection
def add_user(user_data: dict):
    user_data = user_data.copy()
    # Hash the password before storing
    if "password" in user_data:
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
    user_data["created_at"] = user_data.get("created_at", datetime.now())
    user_data["is_active"] = user_data.get("is_active", True)
    user_data["role"] = user_data.get("role", "user")
    result = users_collection.insert_one(user_data)
    return str(result.inserted_id)

# Get user by username
def get_user_by_username(username: str):
    user = users_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        user.pop("_id", None)
    return user

# Get user by email
def get_user_by_email(email: str):
    user = users_collection.find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        user.pop("_id", None)
    return user


def get_all_employees():
    return list(employees_collection.find({}, {"_id": 0}))

# Get employees by department
def get_employees_by_department(department: str):
    return list(employees_collection.find({"department": department}, {"_id": 0}))

# Get employee by id
def get_employee_by_id(employee_id: str):
    return employees_collection.find_one({"employee_id": employee_id}, {"_id": 0})

# POST request handler for adding a new employee
def add_employee(employee_data: dict):
    return employees_collection.insert_one(employee_data)

# PUT request handler for updating an existing employee
def update_employee(employee_id: str, employee_data: dict):
    result = employees_collection.update_one(
        {"employee_id": employee_id},
        {"$set": employee_data},
        upsert=False
    )
    return result.modified_count > 0
