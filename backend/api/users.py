from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from backend.database.functions import get_db_session
from backend.database.tables import UsersTable

from .router_manager import RouterManager

router = RouterManager.add_router(APIRouter(prefix="/users"))


class GetUserItemModel(BaseModel):
    """
    Get users model.
    """
    id: int
    username: str
    email: str

class GetUsersListResponseModel(BaseModel):
    """
    Get users list response model.
    """
    users: list[GetUserItemModel]


@router.get("/", response_model=GetUsersListResponseModel)
async def get_users():
    async with get_db_session() as session:
        result = await session.execute(select(UsersTable))
        users = result.scalars().all()
        users_list = [GetUserItemModel(id=user.id, username=user.username, email=user.email) for user in users]
        return GetUsersListResponseModel(users=users_list)
    
