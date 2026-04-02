from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import secrets
import jwt
import re

# Import from the files we just created in the parent directory
from models import User, get_db
# Import config from dependencies to keep it consistent
from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, redis_client
# Import email function
from utils.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters long.")
        if not re.search(r'[A-Za-z]', v):
            raise ValueError("Password must contain at least one alphabetic letter.")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one numeric digit.")
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError("Password must contain at least one special character.")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict
    
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters long.")
        if not re.search(r'[A-Za-z]', v):
            raise ValueError("Password must contain at least one alphabetic letter.")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one numeric digit.")
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError("Password must contain at least one special character.")
        return v
    

# --- HELPERS ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- ENDPOINTS ---
# REGISTRATION
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check existing
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create User
    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 3. Auto-login (Create Token)
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"email": new_user.email, "id": new_user.id}
    }

# LOGIN
@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Define our Redis keys based on the user's email
    lock_key = f"locked_out:{user_data.email}"
    attempts_key = f"failed_attempts:{user_data.email}"

    # 1. Check if the account is currently serving a 10-minute lockout
    if redis_client.exists(lock_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Account temporarily locked due to multiple failed login attempts. Try again in 10 minutes."
        )
        
    # Get user details from database
    user = db.query(User).filter(User.email == user_data.email).first()
    
    # 2. Verify Credentials
    if not user or not verify_password(user_data.password, user.hashed_password):
        # --- Handle Failed Attempt ---
        attempts = redis_client.incr(attempts_key)
        
        if attempts == 1:
            # First strike: Start the 1-minute countdown window
            redis_client.expire(attempts_key, 60)
            
        if attempts >= 5:
            # Fifth strike: Trigger the 10-minute (600 seconds) lockout and clear the attempts tracker
            redis_client.setex(lock_key, 600, "locked")
            redis_client.delete(attempts_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                detail="Too many failed attempts. Account locked for 10 minutes."
            )
            
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # 3. Handle Successful Login
    # Clear any previous failed attempts so they start with a clean slate
    redis_client.delete(attempts_key)
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {"email": user.email, "id": user.id}
    }

# REQUEST PASSWORD RESET
@router.post("/request-password-reset")
async def request_password_reset(
    payload: PasswordResetRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email).first()
    
    # We always return "success" to prevent email enumeration attacks
    if user:
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        expiration = datetime.utcnow() + timedelta(hours=1) # 1-hour validity
        
        # Save to DB
        user.reset_token = token
        user.reset_token_expires = expiration
        db.commit()
        
        # Send Email (Background Task)
        background_tasks.add_task(send_password_reset_email, user.email, token)
    
    return {"message": "If an account exists, a reset email has been sent."}

# PERFORM PASSWORD RESET
@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    # Find user by the token
    user = db.query(User).filter(User.reset_token == payload.token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
        
    if datetime.utcnow() > user.reset_token_expires:
        # Clean up the expired token before raising the error
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        raise HTTPException(status_code=400, detail="Token has expired. Please request a new one.")
    
    # Update Password
    user.hashed_password = get_password_hash(payload.new_password)
    
    # Clear the token and expiration date so it can't be reused
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password updated successfully."}