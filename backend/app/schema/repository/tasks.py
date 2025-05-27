from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.services.database_service import Base
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
import uuid
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.sql import text

class task(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[uuid.UUID] = None
    task_name: str
    team_id: uuid.UUID
    priority: int
    deadline: Optional[datetime] = None
    points: Optional[int] = None
    date_of_completion: Optional[datetime] = None
    date_of_creation: datetime = None
    description: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            task_name=obj.task_name,
            team_id=obj.team_id,
            deadline=obj.deadline,
            points=obj.points,
            date_of_completion=obj.date_of_completion,
            date_of_creation=obj.date_of_creation,
            priority=obj.priority,
            description=obj.description,
            notes=obj.notes,
        )


class TaskSchema(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_of_creation = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    priority = Column(Integer, nullable=False)
    task_name = Column(Text, nullable=False)
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)
    points = Column(Integer, nullable=True)
    date_of_completion = Column(TIMESTAMP(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
