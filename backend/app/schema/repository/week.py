from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.services.database_service import Base
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
import uuid
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pgvector.sqlalchemy import Vector


class week(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[uuid.UUID] = None
    start_date: datetime
    end_date: datetime
    user_id: uuid.UUID
    summary: Optional[str] = None
    feedback: Optional[str] = None
    collaborators: Optional[List[uuid.UUID]] = None
    missed_deadlines: Optional[List[uuid.UUID]] = None
    completed_tasks: Optional[List[uuid.UUID]] = None
    points_completed: Optional[int] = None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            start_date=obj.start_date,
            end_date=obj.end_date,
            user_id=obj.user_id,
            summary=obj.summary,
            feedback=obj.feedback,
            collaborators=obj.collaborators,
            missed_deadlines=obj.missed_deadlines,
            completed_tasks=obj.completed_tasks,
            points_completed=obj.points_completed,
        )


class WeekSchema(Base):
    __tablename__ = "week"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    summary = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    collaborators = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    missed_deadlines = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    completed_tasks = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    points_completed = Column(Integer, nullable=True)
    embedding = Column(Vector(1536), nullable=True)
