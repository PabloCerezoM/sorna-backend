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
from backend.database.enums.comedians import ComedianStrEnum
from backend.comedians.base import MetaComedian

router = RouterManager.add_router(APIRouter(prefix="/stories", tags=["stories"]))

class GeneratePromptFormModel(BaseModel):
    """
    Generate prompt model.
    """

    prompt: str
    comedian: ComedianStrEnum

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_prompt(
    form: GeneratePromptFormModel,
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Generate a prompt.
    """
    comedian = MetaComedian.get_comedian(form.comedian)

    return comedian.get_context()

class ComedianInfo(BaseModel):
    name: ComedianStrEnum
    name_comedian: str

@router.get("/all_comedians", response_model=list[ComedianInfo])
async def list_comedians(
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Return list of available comedians with their display names.
    """
    comedians_list = []
    for enum_key, comedian_cls in MetaComedian.comedians.items():
        comedians_list.append(
            ComedianInfo(
                name=enum_key,
                name_comedian=comedian_cls.name_comedian,
            )
        )
    return comedians_list

