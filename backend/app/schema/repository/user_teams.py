from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, ForeignKey
import uuid


class user_teams(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_id: uuid.UUID
    team_id: uuid.UUID

    @classmethod
    def from_orm(cls, obj):
        return cls(user_id=obj.user_id, team_id=obj.team_id)


class UserTeamsSchema(Base):
    __tablename__ = "user_teams"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    )
