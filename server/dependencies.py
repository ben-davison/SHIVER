from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import jwt
from jwt.exceptions import PyJWTError
from models import get_db, User
import os
from typing import Optional
from dotenv import load_dotenv
import redis

# Load the .env file
load_dotenv()

# --- CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_dev_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

# --- EMAIL CONFIGURATION ---
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")

# --- CUBE LIMITS PER DAY ---
MAX_CUBES_PER_DAY = 5

# --- REDIS CONFIGURATION ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# If we are on Windows, use the fake in-memory Redis
if os.name == 'nt':
    import fakeredis
    redis_client = fakeredis.FakeRedis(decode_responses=True)
    print("WARNING: Using FakeRedis for local development.")

# Otherwise, connect to the real Redis
else:
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=0, 
        decode_responses=True
    )


# This tells FastAPI that the token comes from the /auth/login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Define a "Soft" OAuth2 scheme that doesn't scream 401 if the token is missing
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# 2. The Optional User Dependency
def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional), 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Returns the User object if a valid token is present.
    Returns None if no token (guest) or invalid token.
    """
    if not token:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except PyJWTError:
        return None

    user = db.query(User).filter(User.email == username).first()
    return user


# --- THE PROTECTION FUNCTION ---
# This is the function you use to protect other routes
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user


# --- TRACK NUMBER OF DATA CUBE REQUESTS PER DAY --- 
def check_daily_cube_limit(user = Depends(get_current_user)):
    """
    Synchronous FastAPI dependency to check daily data cube limits via Redis.
    """
    # 1. Generate a date-specific key. We will use email to match your auth logic.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    redis_key = f"datacubes:{user.email}:{today}"
    
    # 2. Atomically increment the daily count
    # Because you set decode_responses=True in your config, this returns an int
    requests_today = redis_client.incr(redis_key)
    
    # 3. If it's the first request today, set expiration to 24 hours (86400 seconds)
    if requests_today == 1:
        redis_client.expire(redis_key, 86400)
        
    # 4. Check against your limit
    if requests_today > MAX_CUBES_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have reached your daily limit of {MAX_CUBES_PER_DAY} data cubes. Please try again tomorrow."
        )
        
    return True