from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, String
import uuid
from app.core.logger import logger


class team(BaseModel):
    """A team represents a group of users working together on tasks.

    Teams are the organizational units that contain users and tasks. Each team has a unique name
    and can have multiple users as members. Teams provide the context for task collaboration
    and project management.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    team_name: str
    """The unique name of the team. Used for identification and display purposes."""

    id: uuid.UUID
    """Unique identifier for the team. Generated automatically when the team is created."""

    @classmethod
    def from_orm(cls, obj):
        try:
            logger.info(f"Creating team from ORM object: {obj}")
            return cls(team_name=obj.team_name, id=obj.id)
        except Exception as e:
            logger.error(f"Failed to create team from ORM object: {e}")
            raise


class TeamSchema(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_name = Column(String, nullable=False)
