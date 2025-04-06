from datetime import datetime, timedelta
from jose import jwt

# Clave privada para firmar el JWT (ejemplo). En producción,
# guárdala en un lugar seguro (variables de entorno, etc.)
SECRET_KEY = "SECRET_KEY_DE_DESARROLLO_12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Crea un token JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
