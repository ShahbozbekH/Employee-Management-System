from app.utils.utils import verify_jwt_token, require_admin
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.routing import APIRouter
from contextlib import asynccontextmanager
from datetime import timedelta, datetime
from app.config.database import client, employees_collection
from app.routes.employee_routes import router as employee_router
from app.schemas.employee_schema import UserCreate, UserResponse
from app.model.employee_model import add_user, get_user_by_username, get_user_by_email, hash_password
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from app.utils.utils import (
	oauth2_scheme,
	create_access_token,
	verify_jwt_token,
	DEMO_USERNAME,
	DEMO_PASSWORD,
	ACCESS_TOKEN_EXPIRE_MINUTES
)

@asynccontextmanager
async def lifespan(app: FastAPI):
	try:
		info = client.server_info()  # Force connection to check if MongoDB is available
		print("Connected to MongoDB:", info)
	except Exception as e:
		print("Error connecting to MongoDB:", e)
		raise e
	yield

app = FastAPI(title="Employee Management System API", version="1.0.0", lifespan=lifespan)

# CORS setup to allow frontend (Vite) to communicate with backend
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"] ,
	allow_headers=["*"]
)

# Insert an example employee if not present
def insert_example_employee():
	example_employee = {
		"employee_id": "E001",
		"name": "John Doe",
		"email": "john.doe@example.com",
		"department": "Engineering",
		"position": "Software Engineer",
		"status": "Active",
		"created_at": None
	}
	if not employees_collection.find_one({"employee_id": example_employee["employee_id"]}):
		example_employee["created_at"] = datetime.now()
		employees_collection.insert_one(example_employee)

# app.include_router with dependency for basic auth



class SecureAPIRouter(APIRouter):
	def add_api_route(self, path: str, endpoint, *args, **kwargs):
		if not path.startswith("/health"):
			dependencies = kwargs.pop("dependencies", [])
			dependencies.append(Depends(verify_jwt_token))
			kwargs["dependencies"] = dependencies
		super().add_api_route(path, endpoint, *args, **kwargs)

secure_router = SecureAPIRouter()
for route in employee_router.routes:
	secure_router.add_api_route(
		route.path,
		route.endpoint,
		methods=route.methods,
		response_model=getattr(route, "response_model", None),
		status_code=getattr(route, "status_code", None),
		summary=getattr(route, "summary", None),
		description=getattr(route, "description", None),
		response_description=getattr(route, "response_description", None),
		responses=getattr(route, "responses", None),
		tags=getattr(route, "tags", None),
		name=getattr(route, "name", None),
		deprecated=getattr(route, "deprecated", None),
		operation_id=getattr(route, "operation_id", None),
		response_model_include=getattr(route, "response_model_include", None),
		response_model_exclude=getattr(route, "response_model_exclude", None),
		response_model_by_alias=getattr(route, "response_model_by_alias", True),
		response_class=getattr(route, "response_class", None),
		dependencies=getattr(route, "dependencies", None),
		callbacks=getattr(route, "callbacks", None),
		openapi_extra=getattr(route, "openapi_extra", None),
	)
app.include_router(secure_router, prefix="/employees")

# User registration endpoint

# Password strength check (simple: at least 8 chars, 1 digit, 1 uppercase, 1 special)
import re
def is_strong_password(password: str) -> bool:
	if len(password) < 8:
		return False
	if not re.search(r"[A-Z]", password):
		return False
	if not re.search(r"[0-9]", password):
		return False
	if not re.search(r"[^A-Za-z0-9]", password):
		return False
	return True

@app.post("/register", status_code=201)
def register_user(user: UserCreate = Body(...)):
	# Check for required fields (email, username, password)
	if not user.email or not user.username or not user.password:
		raise HTTPException(status_code=422, detail=[{"loc": ["body", "email"], "msg": "Field required", "type": "missing"}])
	if get_user_by_username(user.username):
		raise HTTPException(status_code=409, detail="Username already exists")
	if get_user_by_email(user.email):
		raise HTTPException(status_code=400, detail="Email already exists")
	if not is_strong_password(user.password):
		raise HTTPException(status_code=422, detail={"password": "Password too weak"})
	user_dict = user.model_dump()
	user_id = add_user(user_dict)
	return {
		"message": "User registered successfully",
		"id": user_id,
		"username": user.username,
		"email": user.email,
		"full_name": user.full_name,
		"is_active": True,
		"created_at": datetime.now().isoformat(),
		"role": user.role
	}



# Login endpoint to get JWT token

# Always return 401 for wrong password or nonexistent user
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
	if form_data.username == DEMO_USERNAME and form_data.password == DEMO_PASSWORD:
		role = "admin"
	else:
		user = get_user_by_username(form_data.username)
		if not user or user.get("hashed_password") != hash_password(form_data.password):
			raise HTTPException(status_code=401, detail="Invalid credentials")
		role = user.get("role", "user")
	access_token = create_access_token(
		data={"sub": form_data.username, "role": role},
		expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	)
	return {"access_token": access_token, "token_type": "bearer", "role": role}

@app.get("/protected")
def protected_route(request: Request, token: str = Depends(oauth2_scheme)):
	if not token:
		return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
	try:
		user = verify_jwt_token(token)
	except HTTPException as e:
		if "expired" in str(e.detail).lower() or "invalid" in str(e.detail).lower():
			return JSONResponse(status_code=401, content={"detail": "Token expired or invalid"})
		return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})
	return {"message": "Access granted"}

# Admin-only route
@app.get("/admin")
def admin_route(user=Depends(require_admin)):
	return {"message": "Admin access granted"}

@app.get("/health")
def health_check():
	return {"status": "API is running"}
