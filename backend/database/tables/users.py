from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid
from .base import Base
from .sessions import SessionsTable
from .user_prompts import UserPromptsTable


class UsersTable(Base):
    """
    Users table model.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)
    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default_factory=uuid4)
    _sessions: Mapped[list[SessionsTable]] = relationship(
        SessionsTable,
        cascade="all, delete-orphan",
        default_factory=list,
    )
    _user_prompts: Mapped[list[UserPromptsTable]] = relationship(
        UserPromptsTable,
        cascade="all, delete-orphan",
        default_factory=list,
    )