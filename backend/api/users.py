from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, or_

from backend.api.security import AuthenticatedUser
from backend.database.functions import get_db_session
from backend.database.tables import UsersTable

from .router_manager import RouterManager
from backend.extra.password_utils import verify_password
from backend.extra.jwt_utils import create_access_token
from backend.extra.password_utils import hash_password

router = RouterManager.add_router(APIRouter(prefix="/users"))


class GetUserItemModel(BaseModel):
    """
    Get users model.
    """
    id: UUID
    username: str
    email: str

class GetUsersListResponseModel(BaseModel):
    """
    Get users list response model.
    """
    users: list[GetUserItemModel]

class LoginRequestModel(BaseModel):
    username: str
    password: str

class LoginResponseModel(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CreateUserRequestModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class CreateUserResponseModel(BaseModel):
    id: UUID
    username: str
    email: str

@router.get("/all", response_model=GetUsersListResponseModel)
async def get_users(current_user: Annotated[AuthenticatedUser, Depends()]):
    async with get_db_session() as session:
        result = await session.execute(select(UsersTable))
        users = result.scalars().all()
        users_list = [GetUserItemModel(id=user.id, username=user.username, email=user.email) for user in users]
        return GetUsersListResponseModel(users=users_list)
    
@router.post("/login", response_model=LoginResponseModel)
async def login(login_data: LoginRequestModel):
    """
    Endpoint para loguear al usuario y retornar un JWT.
    """
    async with get_db_session() as session:
        # 1) Buscar si existe el usuario
        stmt = select(UsersTable).where(UsersTable.username == login_data.username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # No existe usuario con ese username
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos."
            )

        # 2) Verificar la contraseña
        if not verify_password(login_data.password, user.password):
            # Contraseña inválida
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos."
            )

        # 3) Crear y devolver un token
        token_data = {"sub": str(user.id)}  # O "sub": user.username
        access_token = create_access_token(data=token_data)

        return LoginResponseModel(access_token=access_token)
    
@router.post("/create", response_model=CreateUserResponseModel)
async def create_user(user_data: CreateUserRequestModel):
    """
    Crea un nuevo usuario, encriptando la contraseña antes de guardarla.
    Retorna un objeto con la información del usuario (sin la contraseña).
    """
    async with get_db_session() as session:
        # 1) Verificar si el username o email ya existen
        stmt = select(UsersTable).where(
            or_(
                UsersTable.username == user_data.username,
                UsersTable.email == user_data.email
            )
        )
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario o email ya existe en el sistema."
            )

        # 2) Crear nueva instancia del modelo UsersTable
        new_user = UsersTable(
            username=user_data.username,
            email=user_data.email,
            password=hash_password(user_data.password),
        )

        # 3) Guardar en la base de datos
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)  # Para obtener el 'id' auto-generado, etc.

        # 4) Retornar la información sin la contraseña
        return CreateUserResponseModel(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
        )