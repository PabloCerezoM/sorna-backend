import uuid
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String
from .base import Base



class SessionsTable(Base):
    """
    Sessions table model.
    """

    __tablename__ = "session"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    session_id: Mapped[str] = mapped_column(
        String(344),
        primary_key=True,
        nullable=False,
    )