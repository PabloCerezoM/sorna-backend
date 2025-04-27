from datetime import datetime

from sqlalchemy import DateTime
from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, ForeignKey, Enum
from backend.database.enums.comedians import ComedianStrEnum
from .base import Base
from .sessions import SessionsTable


class UserPromptsTable(Base):
    """
    User prompts model.
    """

    __tablename__ = "user_prompts"
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    prompt: Mapped[str] = mapped_column(nullable=False)
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    comedian: Mapped[ComedianStrEnum] = mapped_column(Enum(ComedianStrEnum), nullable=False)
    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default_factory=uuid4)