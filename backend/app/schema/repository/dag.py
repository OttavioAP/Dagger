from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, ForeignKey
import uuid
from typing import Dict, List, Any
from app.schema.repository.tasks import task


class DagAdjacencyList(BaseModel):
    dag_id: uuid.UUID
    adjacency_list: Dict[uuid.UUID, list[uuid.UUID]]


class dag(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dag_id: uuid.UUID
    team_id: uuid.UUID
    dag_graph: Dict[uuid.UUID, List[uuid.UUID]]

    @classmethod
    def from_orm(cls, obj):
        return cls(
            dag_id=obj.dag_id,
            team_id=obj.team_id,
            dag_graph=obj.dag_graph,
        )


class DagSchema(Base):
    __tablename__ = "dag"

    dag_id = Column(UUID(as_uuid=True), primary_key=True)
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    dag_graph = Column(UUID(as_uuid=True), nullable=False)
