from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

# pyrefly: ignore [missing-import]
import bcrypt
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from dotenv import load_dotenv
from ..database import get_db
from ..models import User, OTP
from ..schemas import UserCreate, Token, VerifyOTP, ForgotPassword, ResetPassword, GoogleLoginRequest

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Get JWT configuration from environment
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable is not set. Please check your .env file.")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Direct Bcrypt Hashing helper functions
def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", 2))
    expire = datetime.utcnow() + timedelta(hours=expiration_hours)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Dual-Mode SMTP/Mock Email Helper
def send_otp_email(to_email: str, code: str, purpose: str):
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", "noreply@yourdomain.com")
    
    subject = "Verify Your Account - OTP Code" if purpose == "register" else "Reset Your Password - OTP Code"
    body = (
        f"Hello,\n\n"
        f"Your verification code is: {code}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"If you did not make this request, you can safely ignore this email."
    )
    
    # Check if SMTP is configured (runs mock mode if empty/placeholder)
    is_mock = (
        not smtp_username or 
        "your_smtp_username" in smtp_username or 
        smtp_username.strip() == ""
    )
    
    if is_mock:
        print("\n" + "="*60)
        print(f"[MOCK EMAIL SENDER]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"OTP Code: {code}")
        print("="*60 + "\n")
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_from, to_email, msg.as_string())
        server.quit()
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Error sending email via SMTP: {e}. Fallback to printing OTP:")
        print(f"OTP for {to_email}: {code}")

# Google ID Token Verification Helper
def verify_google_id_token(token: str) -> dict:
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    is_mock = (
        not google_client_id or 
        "your_google_client_id" in google_client_id or 
        google_client_id.strip() == ""
    )
    
    if is_mock:
        print(f"[MOCK GOOGLE SIGN-IN] Bypassing Google token verification for token: {token[:10]}...")
        # Generate mock values from token contents
        mock_email = token if "@" in token else "google_user@gmail.com"
        mock_username = mock_email.split("@")[0]
        return {
            "email": mock_email,
            "name": mock_username
        }
        
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        return {
            "email": idinfo['email'],
            "name": idinfo.get('name') or idinfo['email'].split('@')[0]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Google Authentication failed: {e}"
        )

# Routes

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        is_verified=False
    )
    db.add(new_user)
    
    # Generate OTP
    otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Store OTP (cleaning up previous registration OTPs for same email)
    db.query(OTP).filter(OTP.email == user_data.email, OTP.purpose == "register").delete()
    otp_record = OTP(
        email=user_data.email,
        code=otp_code,
        expires_at=expires_at,
        purpose="register"
    )
    db.add(otp_record)
    
    db.commit()
    
    # Send email asynchronously or log it
    send_otp_email(user_data.email, otp_code, "register")
    
    return {"message": "Registration successful. Please verify using the OTP sent to your email."}

@router.post("/verify-otp")
def verify_otp(verify_data: VerifyOTP, db: Session = Depends(get_db)):
    otp_record = db.query(OTP).filter(
        OTP.email == verify_data.email,
        OTP.code == verify_data.code,
        OTP.purpose == verify_data.purpose
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
        
    if otp_record.expires_at < datetime.utcnow():
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP code has expired")
        
    # Mark user verified if register purpose
    if verify_data.purpose == "register":
        user = db.query(User).filter(User.email == verify_data.email).first()
        if user:
            user.is_verified = True
            db.commit()
            
    # Remove OTP record
    db.delete(otp_record)
    db.commit()
    
    return {"message": f"OTP verification for '{verify_data.purpose}' succeeded."}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Fallback to check email login
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
        
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Account not verified. Please verify using OTP first.")
        
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(forgot_data: ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == forgot_data.email).first()
    if not user:
        # Return generic message to prevent user enumeration
        return {"message": "If the email exists in our records, an OTP code has been sent."}
        
    # Generate OTP
    otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Store OTP
    db.query(OTP).filter(OTP.email == forgot_data.email, OTP.purpose == "reset").delete()
    otp_record = OTP(
        email=forgot_data.email,
        code=otp_code,
        expires_at=expires_at,
        purpose="reset"
    )
    db.add(otp_record)
    db.commit()
    
    # Send email
    send_otp_email(forgot_data.email, otp_code, "reset")
    
    return {"message": "If the email exists in our records, an OTP code has been sent."}

@router.post("/reset-password")
def reset_password(reset_data: ResetPassword, db: Session = Depends(get_db)):
    otp_record = db.query(OTP).filter(
        OTP.email == reset_data.email,
        OTP.code == reset_data.code,
        OTP.purpose == "reset"
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
        
    if otp_record.expires_at < datetime.utcnow():
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP code has expired")
        
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Reset password securely
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.is_verified = True  # Ensure verified if password is reset
    
    # Clean up
    db.delete(otp_record)
    db.commit()
    
    return {"message": "Password has been successfully updated."}

@router.post("/google-login", response_model=Token)
def google_login(login_data: GoogleLoginRequest, db: Session = Depends(get_db)):
    # Verify the Google ID Token
    google_info = verify_google_id_token(login_data.id_token)
    email = google_info["email"]
    name = google_info["name"]
    
    # Check if user already exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Check if username already exists, if so generate a unique one
        base_username = name
        username = base_username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        # Automatically register a new user (with Google OAuth, email is verified immediately)
        # Generate a random password since they login with Google
        random_pass = secrets.token_hex(16)
        hashed_pwd = get_password_hash(random_pass)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_pwd,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    # Generate token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "is_verified": current_user.is_verified
    }