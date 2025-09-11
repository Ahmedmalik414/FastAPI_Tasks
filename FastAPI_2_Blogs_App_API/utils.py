from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone 
from jose import JWTError, jwt
from database import SessionLocal
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


SECRET_KEY = "sk-03345265362"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))  # updated
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)