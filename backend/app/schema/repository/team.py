from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, String
import uuid


class team(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    team_name: str
    id: uuid.UUID

    @classmethod
    def from_orm(cls, obj):
        return cls(team_name=obj.team_name, id=obj.id)


class TeamSchema(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_name = Column(String, nullable=False)
