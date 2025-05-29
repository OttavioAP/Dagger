from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schema.repository.dag import DagSchema, dag
from app.core.logger import logger
import uuid
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
from app.services.graph_service import (
    find_connected_nodes,
    split_graph,
    merge_graphs,
    connected_components,
)
from app.core.logger import logger


@dataclass
class EdgeOperationResult:
    dag_id: uuid.UUID
    new_dag_id: Optional[uuid.UUID] = None


class DagRepository:
    def __init__(self):
        self.model = DagSchema

    async def get_dag(self, db: AsyncSession, dag_id: uuid.UUID) -> dag:
        try:
            logger.info(f"Fetching DAG {dag_id}")
            result = await db.execute(
                select(DagSchema).where(DagSchema.dag_id == dag_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                logger.warning(f"DAG {dag_id} not found")
                raise HTTPException(status_code=404, detail="DAG not found")
            logger.info(f"Fetched DAG {dag_id}")
            return dag(dag_id=obj.dag_id, team_id=obj.team_id, dag_graph=obj.dag_graph)
        except Exception as e:
            logger.error(f"Error fetching DAG {dag_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error fetching DAG {dag_id}: {e}"
            )

    async def get_dags_by_team(self, db: AsyncSession, team_id: uuid.UUID):
        try:
            logger.info(f"Fetching DAGs for team {team_id}")
            result = await db.execute(
                select(DagSchema).where(DagSchema.team_id == team_id)
            )
            objs = result.scalars().all()
            dags = []
            for obj in objs:
                dags.append(
                    dag(dag_id=obj.dag_id, team_id=obj.team_id, dag_graph=obj.dag_graph)
                )
            return dags
        except Exception as e:
            logger.error(f"Error fetching DAGs for team {team_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error fetching DAGs for team {team_id}: {e}"
            )

    async def get_all_dags(self, db: AsyncSession) -> List[dag]:
        try:
            logger.info(f"Fetching all DAGs")
            result = await db.execute(select(DagSchema))
            objs = result.scalars().all()
            dags = []
            for obj in objs:
                dags.append(
                    dag(dag_id=obj.dag_id, team_id=obj.team_id, dag_graph=obj.dag_graph)
                )
            return dags
        except Exception as e:
            logger.error(f"Error fetching all DAGs: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error fetching all DAGs: {e}")

    async def add_edges(
        self,
        db: AsyncSession,
        first_task_id: uuid.UUID,
        dependencies: list[uuid.UUID],
        team_id: uuid.UUID,
    ):
        try:
            logger.info(
                f"Adding edges from {first_task_id} to {dependencies} for team {team_id}"
            )
            involved_task_ids = set(
                [str(first_task_id)] + [str(dep) for dep in dependencies]
            )
            result = await db.execute(select(DagSchema))
            dags = result.scalars().all()
            dag_map = {}
            for dag_obj in dags:
                dag_graph = dag_obj.dag_graph
                for tid in involved_task_ids:
                    if tid in dag_graph:
                        dag_map[tid] = dag_obj
            involved_dags = set(dag_map.values())
            if not involved_dags:
                # No existing DAG, create new
                dag_graph = {str(first_task_id): [str(dep) for dep in dependencies]}
                for dep in dependencies:
                    dag_graph.setdefault(str(dep), [])
                new_dag = DagSchema(team_id=team_id, dag_graph=dag_graph)
                db.add(new_dag)
                await db.commit()
                await db.refresh(new_dag)
                logger.info(f"Created new DAG {new_dag.dag_id}")
                return {"dag_id": new_dag.dag_id}
            else:
                # Merge all involved DAGs into one
                merged_graph = {}
                for dag_obj in involved_dags:
                    merged_graph.update(dag_obj.dag_graph)
                # Add all edges
                merged_graph.setdefault(str(first_task_id), [])
                for dep in dependencies:
                    merged_graph.setdefault(str(dep), [])
                    if str(dep) not in merged_graph[str(first_task_id)]:
                        merged_graph[str(first_task_id)].append(str(dep))
                # Remove old DAGs
                for dag_obj in involved_dags:
                    await db.delete(dag_obj)
                # Create new merged DAG
                new_dag = DagSchema(team_id=team_id, dag_graph=merged_graph)
                db.add(new_dag)
                await db.commit()
                await db.refresh(new_dag)
                logger.info(f"Merged DAGs into new DAG {new_dag.dag_id}")
                return {"dag_id": new_dag.dag_id}
        except Exception as e:
            logger.error(
                f"Error adding edges from {first_task_id} to {dependencies} for team {team_id}: {e}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=f"Error adding edges: {e}")

    async def delete_edges(
        self,
        db: AsyncSession,
        dag_id: uuid.UUID,
        first_task_id: uuid.UUID,
        dependencies: list[uuid.UUID],
    ):
        try:
            logger.info(
                f"Deleting edges from {first_task_id} to {dependencies} in DAG {dag_id}"
            )
            result = await db.execute(
                select(DagSchema).where(DagSchema.dag_id == dag_id)
            )
            dag_obj = result.scalar_one_or_none()
            if not dag_obj:
                raise HTTPException(status_code=404, detail="DAG not found")
            dag_graph = dag_obj.dag_graph
            first = str(first_task_id)
            # Remove edges
            for dep in dependencies:
                dep_str = str(dep)
                if first in dag_graph and dep_str in dag_graph[first]:
                    dag_graph[first].remove(dep_str)
                else:
                    logger.error(
                        f"Edge from {first} to {dep_str} not found in DAG {dag_id} during delete_edges operation."
                    )
                    raise HTTPException(
                        status_code=404,
                        detail=f"Edge from {first} to {dep_str} not found in DAG {dag_id}",
                    )
            # Check for disconnected components (split)
            components = connected_components(dag_graph)

            # Remove empty nodes (no outgoing or incoming edges)
            def has_edges(node, graph):
                return bool(graph.get(node, [])) or any(
                    node in v for v in graph.values()
                )

            # Remove the old DAG
            await db.delete(dag_obj)
            new_dag_ids = []
            for comp in components:
                # Only keep nodes with edges
                new_graph = {
                    n: [d for d in dag_graph[n] if d in comp]
                    for n in comp
                    if has_edges(n, dag_graph)
                }
                if new_graph:
                    new_dag = DagSchema(team_id=dag_obj.team_id, dag_graph=new_graph)
                    db.add(new_dag)
                    await db.commit()
                    await db.refresh(new_dag)
                    new_dag_ids.append(new_dag.dag_id)
            logger.info(f"Deleted edges and created new DAGs: {new_dag_ids}")
            return {"new_dag_ids": new_dag_ids}
        except Exception as e:
            logger.error(
                f"Error deleting edges from {first_task_id} to {dependencies} in DAG {dag_id}: {e}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=f"Error deleting edges: {e}")
