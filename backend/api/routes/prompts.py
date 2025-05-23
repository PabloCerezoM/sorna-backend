import json
from uuid import UUID
from typing import Annotated

import bcrypt
from openai import OpenAI
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, StringConstraints, Field
from sqlalchemy import func, select, insert

from backend.settings.openai import OpenaiSettings
from backend.database.functions import get_db_session
from backend.database.tables import UsersTable, SessionsTable
from backend.api.security import get_authenticated_user, AuthenticatedUser
from backend.api.router_manager import RouterManager
from backend.api.security import SessionMiddleware
from backend.database.enums.comedians import ComedianStrEnum
from backend.database.tables import UserPromptsTable  
from backend.comedians.base import MetaComedian
from backend.database.functions import get_db_session

router = RouterManager.add_router(APIRouter(prefix="/stories", tags=["stories"]))

class GeneratePromptFormModel(BaseModel):
    """
    Generate prompt model.
    """

    prompt: str
    comedian: ComedianStrEnum

class GeneratePromptResponseModel(BaseModel):
    """
    Generate prompt response model.
    """
    title: str
    story: str
    comedian: ComedianStrEnum
    date_created: str

@router.post("/generate", response_model=GeneratePromptResponseModel, status_code=status.HTTP_201_CREATED)
async def generate_prompt(
    form: GeneratePromptFormModel,
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Generate a prompt.
    """
    comedian = MetaComedian.get_comedian(form.comedian)
    if not comedian:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comedian not found",
        )
    prompt = form.prompt
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt is required",
        )
    prompt_to_generate = comedian.get_context() + prompt
    
    client = OpenAI(api_key=OpenaiSettings().OPENAI_API_KEY)
    if not client.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not set",
        )
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres un asistente que responde solo en formato JSON válido."},
            {"role": "user", "content": (
                "Tu respuesta debe ser un objeto JSON válido con exactamente dos claves: "
                "\"title\" y \"story\". Ambas claves deben estar presentes SIEMPRE. "
                "\"title\" debe ser una cadena corta y descriptiva del contenido de la historia. "
                "\"story\" debe ser una cadena que contenga la historia generada. "
                "No incluyas ningún texto fuera del objeto JSON. No uses bloques de código. "
                "Ejemplo de formato: {\"title\": \"El despertar\", \"story\": \"Un día, el sol no salió...\"}"
            )},
            {"role": "user", "content": prompt_to_generate}
        ],
        max_tokens=1024,
        temperature=0.7,
    )
    story = response.choices[0].message.content or "No story generated"
    story_response = json.loads(story)


    new_prompt = UserPromptsTable(
        user_id=current_user.id,
        prompt=prompt,
        comedian=form.comedian,
        date_created=func.now(),
        title=story_response.get("title", "No title generated"),
        story=story_response.get("story", "No story generated"),
    )

    async with get_db_session() as session:
        session.add(new_prompt)
        await session.commit()
        await session.refresh(new_prompt)

    return GeneratePromptResponseModel(
        title=story_response.get("title", "No title generated"),
        story=story_response.get("story", "No story generated"),
        comedian=form.comedian,
        date_created=new_prompt.date_created.isoformat(),
    )

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

class GetStoryHistoryModel(BaseModel):
    """
    Get stories history model.
    """
    id: UUID
    prompt: str
    comedian: ComedianStrEnum
    date_created: str
    title: str
    story: str

@router.get("/history", response_model=list[GetStoryHistoryModel])
async def get_story_history(
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Get story history.
    """
    async with get_db_session() as session:
        result = await session.execute(
            select(UserPromptsTable)
            .where(UserPromptsTable.user_id == current_user.id)
            .order_by(UserPromptsTable.date_created.desc())
        )
        stories = result.scalars().all()
        return [
            GetStoryHistoryModel(
                id=story.id,
                prompt=story.prompt,
                comedian=story.comedian,
                date_created=story.date_created.isoformat(),
                title=story.title,
                story=story.story,
            )
            for story in stories
        ]
    
@router.delete("/delete/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)],
):
    """
    Delete a story.
    """
    async with get_db_session() as session:
        result = await session.execute(
            select(UserPromptsTable)
            .where(UserPromptsTable.id == story_id, UserPromptsTable.user_id == current_user.id)
        )
        story = result.scalars().first()
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found",
            )
        await session.delete(story)
        await session.commit()
        return {"detail": "Story deleted successfully"}
    
