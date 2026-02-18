from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import secrets
import jwt

# Import from the files we just created in the parent directory
from models import User, get_db
# Import config from dependencies to keep it consistent
from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
# Import email function
from utils.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str

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
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
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
        
        # Save to DB
        user.reset_token = token
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
    
    # Update Password
    user.hashed_password = get_password_hash(payload.new_password)
    
    # Clear the token so it can't be used again
    user.reset_token = None
    db.commit()
    
    return {"message": "Password updated successfully."}