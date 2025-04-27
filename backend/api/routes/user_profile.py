from uuid import UUID
from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, StringConstraints, Field
from sqlalchemy import select

from backend.database.functions import get_db_session
from backend.database.tables import UsersTable, SessionsTable
from backend.api.security import get_authenticated_user, AuthenticatedUser
from backend.api.router_manager import RouterManager
from backend.api.security import SessionMiddleware

router = RouterManager.add_router(APIRouter(prefix="/user_profile", tags=["user_profile"]))


class GetUserProfileModel(BaseModel):
    """
    Get users model.
    """

    id: UUID
    username: str
    email: str


@router.get("", response_model=GetUserProfileModel, status_code=status.HTTP_200_OK)
async def get_user_profile(
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Get user profile.
    """
    async with get_db_session() as session:
        result = await session.execute(select(UsersTable).where(UsersTable.id == current_user.id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return GetUserProfileModel(id=user.id, username=user.username, email=user.email)


class UpdateUserProfileFormModel(BaseModel):
    """
    Update user profile model.
    """

    username: str
    email: str
    password: Annotated[str | None, StringConstraints(min_length=6), Field(None)]


@router.put("", response_model=GetUserProfileModel, status_code=status.HTTP_200_OK)
async def update_user_profile(
    form: UpdateUserProfileFormModel,
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Update user profile.
    """
    async with get_db_session() as session:
        result = await session.execute(
            select(UsersTable)
            .where(
                UsersTable.id != current_user.id,
                (UsersTable.username == form.username) | (UsersTable.email == form.email),
            )
            .limit(1)
        )
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )
        
        result = await session.execute(select(UsersTable).where(UsersTable.id == current_user.id))
        db_user = result.scalars().first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        db_user.username = form.username
        db_user.email = form.email

        if form.password:
            new_password = bcrypt.hashpw(form.password.encode("utf-8"), bcrypt.gensalt())
            db_user.password = new_password

        await session.commit()
        await session.refresh(db_user)
        return GetUserProfileModel(id=db_user.id, username=db_user.username, email=db_user.email)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Delete user profile.
    """
    async with get_db_session() as session:
        result = await session.execute(select(UsersTable).where(UsersTable.id == current_user.id).limit(1))
        db_user = result.scalars().first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        await session.delete(db_user)
        await session.commit()
        return SessionMiddleware.logout(current_user)