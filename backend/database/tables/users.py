import uuid
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from .base import Base


class UsersTable(Base):
    """
    Users table model.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    id: Mapped[UUID] = mapped_column(
        Uuid(),
        primary_key=True,
        default_factory=uuid.uuid4
    )