from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import Base
from sqlalchemy import Column, ForeignKey
import uuid
from typing import Dict, List
from app.schema.repository.tasks import task


class DagAdjacencyList(BaseModel):
    dag_id: uuid.UUID
    adjacency_list: Dict[uuid.UUID, list[uuid.UUID]]


class dag(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dag_id: uuid.UUID
    team_id: uuid.UUID
    DagAdjacencyList: DagAdjacencyList
    tasks: List[task]

    @classmethod
    def from_orm(cls, obj):
        return cls(
            dag_id=obj.dag_id, from_task_id=obj.from_task_id, to_task_id=obj.to_task_id
        )


class DagSchema(Base):
    __tablename__ = "dag"

    dag_id = Column(
        UUID(as_uuid=True), ForeignKey("dags.id", ondelete="CASCADE"), primary_key=True
    )
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    )
    from_task_id = Column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    to_task_id = Column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
