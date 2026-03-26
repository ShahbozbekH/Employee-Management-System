#Defines Employee schema for data validation and serialization
from pydantic import BaseModel, EmailStr
from datetime import datetime

# User schema
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    hashed_password: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    role: str = "user"  # 'admin' or 'user'

# User creation schema (for registration, password in plain text)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str
    role: str = "user"  # 'admin' or 'user'

# User response schema (for API responses)
class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    created_at: datetime
    role: str

class Employee(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    department: str
    position: str
    status: str



class EmployeeResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    department: str
    created_at: datetime


# Response schema for POST/PUT endpoints
class EmployeeMessageResponse(BaseModel):
    message: str
    employee: EmployeeResponse

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    department: str
    position: str
    status: str
    created_at: datetime = datetime.now()