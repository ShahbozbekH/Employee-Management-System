# Authentication-related functions and variables moved from main.py
import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Demo credentials (move to DB for production)
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "admin")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "password")

def custom_unauthorized_exception(request: Request, exc):
	raise HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now(timezone.utc) + expires_delta
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt

def verify_jwt_token(token: str = Depends(oauth2_scheme)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	if not token:
		raise credentials_exception
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		role: str = payload.get("role", "user")
		if username is None:
			raise credentials_exception
	except jwt.ExpiredSignatureError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token expired or invalid",
			headers={"WWW-Authenticate": "Bearer"},
		)
	except JWTError:
		raise credentials_exception
	return {"username": username, "role": role}


def require_admin(user=Depends(verify_jwt_token)):
	if user["role"] != "admin":
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
	return user
