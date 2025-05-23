from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
import uuid
from typing import Optional


class user_tasks(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: uuid.UUID
    task_id: uuid.UUID
    assigned_at: Optional[str] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            user_id=obj.user_id,
            task_id=obj.task_id,
            assigned_at=obj.assigned_at,
        )


class UserTasksSchema(Base):
    __tablename__ = "user_tasks"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    task_id = Column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at = Column(TIMESTAMP(timezone=True), nullable=True)
