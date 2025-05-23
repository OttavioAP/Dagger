from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schema.repository.dag import DagSchema, dag
from app.core.logger import logger
import uuid
import json


class DagRepository:
    def __init__(self):
        self.model = DagSchema

    async def get_dag(self, db: AsyncSession, dag_id: uuid.UUID) -> dag:
        try:
            result = await db.execute(
                select(DagSchema).where(DagSchema.dag_id == dag_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                logger.warning(f"DAG {dag_id} not found")
                raise HTTPException(status_code=404, detail="DAG not found")
            logger.info(f"Fetched DAG {dag_id}")
            dag_graph = json.loads(obj.dag_graph)
            return dag(dag_id=obj.dag_id, dag_graph=dag_graph)
        except Exception as e:
            logger.error(f"Error fetching DAG {dag_id}: {e}")
            raise

    async def create_dag(
        self,
        db: AsyncSession,
        dag_id: uuid.UUID,
        first_task_id: uuid.UUID,
        second_task_id: uuid.UUID,
    ) -> dag:
        try:
            # Create adjacency list with a single edge: first_task_id -> [second_task_id]
            dag_graph = {
                str(first_task_id): [str(second_task_id)],
                str(second_task_id): [],
            }
            new_dag = DagSchema(dag_id=dag_id, dag_graph=json.dumps(dag_graph))
            db.add(new_dag)
            await db.commit()
            await db.refresh(new_dag)
            logger.info(
                f"Created DAG {dag_id} with edge {first_task_id} -> {second_task_id}"
            )
            return dag(dag_id=new_dag.dag_id, dag_graph=dag_graph)
        except Exception as e:
            logger.error(f"Error creating DAG {dag_id}: {e}")
            raise

    async def update_dag_graph(
        self, db: AsyncSession, dag_id: uuid.UUID, new_graph: dict
    ) -> dag:
        try:
            result = await db.execute(
                select(DagSchema).where(DagSchema.dag_id == dag_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                logger.warning(f"DAG {dag_id} not found for update")
                raise HTTPException(status_code=404, detail="DAG not found")
            await db.execute(
                update(DagSchema)
                .where(DagSchema.dag_id == dag_id)
                .values(dag_graph=json.dumps(new_graph))
            )
            await db.commit()
            logger.info(f"Updated dag_graph for DAG {dag_id}")
            await db.refresh(obj)
            return dag(dag_id=obj.dag_id, dag_graph=new_graph)
        except Exception as e:
            logger.error(f"Error updating dag_graph for DAG {dag_id}: {e}")
            raise

    async def delete_dag(self, db: AsyncSession, dag_id: uuid.UUID) -> None:
        try:
            result = await db.execute(
                select(DagSchema).where(DagSchema.dag_id == dag_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                logger.warning(f"DAG {dag_id} not found for delete")
                raise HTTPException(status_code=404, detail="DAG not found")
            await db.delete(obj)
            await db.commit()
            logger.info(f"Deleted DAG {dag_id}")
        except Exception as e:
            logger.error(f"Error deleting DAG {dag_id}: {e}")
            raise

    async def delete_edge(
        self,
        db: AsyncSession,
        dag_id: uuid.UUID,
        first_task_id: uuid.UUID,
        second_task_id: uuid.UUID,
    ) -> None:
        try:
            result = await db.execute(
                select(DagSchema).where(DagSchema.dag_id == dag_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                logger.warning(f"DAG {dag_id} not found for delete_edge")
                raise HTTPException(status_code=404, detail="DAG not found")
            dag_graph = json.loads(obj.dag_graph)
            first = str(first_task_id)
            second = str(second_task_id)
            # Remove the edge if it exists
            if first in dag_graph and second in dag_graph[first]:
                dag_graph[first].remove(second)
            # Count total edges
            edge_count = sum(len(targets) for targets in dag_graph.values())
            if edge_count == 0:
                await self.delete_dag(db, dag_id)
                logger.info(f"DAG {dag_id} deleted after last edge removed")
            else:
                await db.execute(
                    update(DagSchema)
                    .where(DagSchema.dag_id == dag_id)
                    .values(dag_graph=json.dumps(dag_graph))
                )
                await db.commit()
                logger.info(
                    f"Edge {first_task_id} -> {second_task_id} deleted from DAG {dag_id}"
                )
        except Exception as e:
            logger.error(
                f"Error deleting edge {first_task_id} -> {second_task_id} from DAG {dag_id}: {e}"
            )
            raise


# Note: The existence of both dag (Pydantic model) and DagSchema (SQLAlchemy model) is common in FastAPI projects.
# dag is used for data validation/serialization (API), while DagSchema is the ORM model for DB operations.
# You can use only one if you don't need both, but using both is best practice for clear separation of concerns.
