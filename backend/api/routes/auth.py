from uuid import UUID
from typing import Annotated

import bcrypt
from sqlalchemy import select
from fastapi import APIRouter, Depends, Request, status, HTTPException
from pydantic import BaseModel, StringConstraints

from backend.api.security import get_authenticated_user, AuthenticatedUser, SessionMiddleware
from backend.api.router_manager import RouterManager
from backend.database.functions import get_db_session
from backend.database.tables import UsersTable

router = RouterManager.add_router(APIRouter(prefix="/auth", tags=["auth"]))


class LoginForm(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)]
    password: str


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(request: Request, form: LoginForm):
    return await SessionMiddleware.login(
        request=request,
        username=form.username,
        password=form.password,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)]):
    return await SessionMiddleware.logout(current_user)

class RegisterFormModel(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)]
    password: str
    email: Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)]

class RegisterResponseModel(BaseModel):
    id: UUID
    username: str
    email: str

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponseModel)
async def register(form: RegisterFormModel) -> RegisterResponseModel:
    async with get_db_session() as session:
        # Check if the username or email already exists
        existing_user = await session.execute(
            select(UsersTable).where(
                (UsersTable.username == form.username) | (UsersTable.email == form.email)
            ).limit(1)
        )
        existing_user = existing_user.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )
        user_pwd = bcrypt.hashpw(form.password.encode("utf-8"), bcrypt.gensalt())
        new_user = UsersTable(
            username=form.username,
            password=user_pwd,
            email=form.email,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return RegisterResponseModel(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
        )