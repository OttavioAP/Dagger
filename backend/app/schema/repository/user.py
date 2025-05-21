from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, String
import uuid


class user(BaseModel):
    username: str
    id: UUID

    @classmethod
    def from_orm(cls, obj):
        return cls(username=obj.username, id=obj.id)


class UserSchema(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String, nullable=False)
