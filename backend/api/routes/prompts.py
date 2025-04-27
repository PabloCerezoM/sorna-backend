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

router = RouterManager.add_router(APIRouter(prefix="/prompts", tags=["prompts"]))

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