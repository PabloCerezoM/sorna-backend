from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    Hashea la contraseña en texto plano usando bcrypt.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que la contraseña en texto plano coincida con el hash almacenado.
    """
    return pwd_context.verify(plain_password, hashed_password)
