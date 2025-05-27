from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, String, ForeignKey
import uuid


class user(BaseModel):
    """A user represents a team member in the system.
    
    Users are the individual participants who work on tasks within teams. Each user must belong
    to exactly one team, and can collaborate on tasks within that team. Users are identified
    by their unique username and UUID.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: str
    """The unique display name of the user. Used for identification and display purposes."""

    team_id: uuid.UUID
    """The ID of the team this user belongs to. Users can only be members of one team at a time."""

    id: uuid.UUID
    """Unique identifier for the user. Generated automatically when the user is created."""

    @classmethod
    def from_orm(cls, obj):
        return cls(username=obj.username, id=obj.id)


class UserSchema(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
