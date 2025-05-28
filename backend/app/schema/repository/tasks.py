from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from app.services.database_service import Base
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
import uuid
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.sql import text
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"


class TaskFocus(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class task(BaseModel):
    """A task represents a unit of work assigned to a team.

    Tasks are the fundamental building blocks of project management, containing information about
    what needs to be done, when it needs to be done, and how important it is. Each task belongs
    to a team and can be worked on by team members.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[uuid.UUID] = None
    """Unique identifier for the task. Generated automatically if not provided."""

    task_name: str
    """The name/title of the task. Should be concise but descriptive."""

    team_id: uuid.UUID
    """The ID of the team this task belongs to. All collaborators must be members of this team."""

    priority: TaskPriority = TaskPriority.LOW
    """The urgency level of the task. Can be:
    - LOW: Not urgent, can be done when convenient
    - MEDIUM: Important but not critical
    - HIGH: Urgent, should be addressed soon
    - EMERGENCY: Critical, needs immediate attention"""

    focus: TaskFocus = TaskFocus.LOW
    """The level of concentration required to complete the task. Can be:
    - LOW: Can be done with minimal focus, possibly alongside other tasks
    - MEDIUM: Requires moderate focus and attention
    - HIGH: Requires deep focus and should be done without distractions"""

    deadline: Optional[datetime] = None
    """The date and time by which the task should be completed. Optional."""

    points: Optional[int] = None
    """Optional point value assigned to the task, typically used for effort estimation or scoring."""

    date_of_completion: Optional[datetime] = None
    """The date and time when the task was marked as completed. Null if task is still pending."""

    date_of_creation: datetime = None
    """The date and time when the task was created. Automatically set to current timestamp."""

    description: Optional[str] = None
    """Detailed description of the task written by the project manager.
    Should include requirements, objectives, and any other relevant information."""

    notes: Optional[str] = None
    """Additional notes and comments from team members working on the task.
    Can include progress updates, questions, or other relevant information from collaborators."""

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
            focus=obj.focus,
            description=obj.description,
            notes=obj.notes,
        )


class TaskSchema(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_of_creation = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    priority = Column(ENUM(TaskPriority), nullable=False, default=TaskPriority.LOW)
    focus = Column(ENUM(TaskFocus), nullable=False, default=TaskFocus.LOW)
    task_name = Column(Text, nullable=False)
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    deadline = Column(TIMESTAMP(timezone=True), nullable=True)
    points = Column(Integer, nullable=True)
    date_of_completion = Column(TIMESTAMP(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
