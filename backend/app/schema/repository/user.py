from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, String, ForeignKey
import uuid


class user(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: str
    team_id: uuid.UUID
    id: uuid.UUID

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
