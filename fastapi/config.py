from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///database.db"

# Настройки для JWT
SECRET_KEY = "aosidj342390AOKPLSDopk2390$@()2ji1[23-0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")