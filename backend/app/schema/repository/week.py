from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.services.database_service import Base
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
import uuid
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pgvector.sqlalchemy import Vector


class week(BaseModel):
    """A model representing a weekly summary of a user's productivity and accomplishments.
    
    This model captures a week's worth of work activity, including tasks completed,
    collaboration metrics, and AI-generated feedback to improve productivity.
    Each week spans from start_date to end_date (7 days later).
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[uuid.UUID] = None
    start_date: datetime = Field(description="The start date of the week")
    end_date: datetime = Field(description="The end date of the week (7 days after start_date)")
    user_id: uuid.UUID = Field(description="The ID of the user whose productivity is being summarized")
    summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the week's work and productivity patterns"
    )
    feedback: Optional[str] = Field(
        default=None,
        description="AI-generated feedback aimed at improving worker productivity"
    )
    collaborators: Optional[List[uuid.UUID]] = Field(
        default=None,
        description="List of user IDs who were assigned roles on tasks during this week"
    )
    missed_deadlines: Optional[List[uuid.UUID]] = Field(
        default=None,
        description="List of task IDs where deadlines were missed during this week"
    )
    completed_tasks: Optional[List[uuid.UUID]] = Field(
        default=None,
        description="List of task IDs that were completed during this week"
    )
    points_completed: Optional[int] = Field(
        default=None,
        description="Total points completed, where points represent estimated hours of work"
    )

    @classmethod
    def from_orm(cls, obj):
        """Create a week instance from an ORM object.
        
        Args:
            obj: The ORM object containing week data
            
        Returns:
            week: A new week instance populated with data from the ORM object
        """
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
