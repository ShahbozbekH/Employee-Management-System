from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import client, employees_collection
from app.routes.employee_routes import router as employee_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        info = client.server_info()  # Force connection to check if MongoDB is available
        print("Connected to MongoDB:", info)

    except Exception as e:
        print("Error connecting to MongoDB:", e)
        raise e
    # Initialize resources here
    yield
    # Cleanup resources here



app = FastAPI(title="Employee Management System API", version="1.0.0", lifespan=lifespan)

# Insert an example employee if not present
def insert_example_employee():
    from app.config.database import employees_collection
    example_employee = {
        "employee_id": "E001",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "department": "Engineering",
        "position": "Software Engineer",
        "status": "Active",
        "created_at": None
    }
    # Check if already exists
    if not employees_collection.find_one({"employee_id": example_employee["employee_id"]}):
        from datetime import datetime
        example_employee["created_at"] = datetime.now()
        employees_collection.insert_one(example_employee)

# Call insert_example_employee at startup
#insert_example_employee()

#Include employee routes
app.include_router(employee_router, prefix="/employees")

@app.get("/health")
def health_check():
    return {"status": "API is running"}