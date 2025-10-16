from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone 
from jose import JWTError, jwt
from database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status
from models import User
from sqlalchemy.orm import Session
import models
from fastapi import Request, Cookie
from jose.exceptions import ExpiredSignatureError










def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_pwd(password:str)->str:
    return pwd_context.hash(password)

def verify_hashed_pwd(plain_password:str,hashed_pwd:str)->bool:
    return pwd_context.verify(plain_password,hashed_pwd)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = "sk-03345265362"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_current_user(token: str = Depends(oauth2_scheme),db:Session=Depends(get_database)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user   
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    
    
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) 
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)    




def require_admin(current_user : User= Depends(get_current_user)):
    
    if  current_user.role !="admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="only admins are allowed")
    
    return current_user


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])



def get_current_user_with_refresh(
    request: Request,
    db: Session = Depends(get_database),
    token: str = Depends(oauth2_scheme),
    refresh_token: str = Cookie(None)
):
    try:
      
        payload = decode_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid access token")
    except ExpiredSignatureError:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Session expired, please login again")
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        # Create new access token
        new_access_token = create_access_token({"sub": payload["sub"], "role": payload.get("role")})
        email = payload["sub"]
        request.state.new_access_token = new_access_token  

    # Lookup user
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
        
        
        