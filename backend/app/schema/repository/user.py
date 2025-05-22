from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, String
import uuid


class user(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: str
    id: uuid.UUID

    @classmethod
    def from_orm(cls, obj):
        return cls(username=obj.username, id=obj.id)


class UserSchema(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
