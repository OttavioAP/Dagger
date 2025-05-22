from sqlalchemy import select, insert, delete, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.repository.base_repository import BaseRepository
from app.schema.repository.dag import DagSchema, dag, DagAdjacencyList
from fastapi import HTTPException
from app.core.logger import logger
from sqlalchemy.orm import Session
import uuid
import json
from app.schema.repository.tasks import task as TaskModel
from app.core.repository.task_repository import TasksRepository


class DagRepository(BaseRepository[DagSchema]):
    def __init__(self):
        super().__init__(DagSchema)

    async def add_edge(
        self,
        db: AsyncSession,
        dag_id: uuid.UUID,
        from_task_id: uuid.UUID,
        to_task_id: uuid.UUID,
    ) -> DagAdjacencyList:
        async with db.begin():
            await db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
            await db.execute(text("LOCK TABLE dag IN EXCLUSIVE MODE"))
            graph = await self._get_adjacency_list_for_dag(db, dag_id)
            if to_task_id not in graph.get(from_task_id, []):
                graph.setdefault(from_task_id, []).append(to_task_id)
            if self._creates_cycle_in_memory(graph, from_task_id):
                logger.warning(
                    f"Cycle detected when adding edge {from_task_id}->{to_task_id} in DAG {dag_id}"
                )
                raise HTTPException(
                    status_code=400, detail="Adding this edge would create a cycle."
                )
            await db.execute(
                insert(DagSchema).values(
                    dag_id=dag_id, from_task_id=from_task_id, to_task_id=to_task_id
                )
            )
            await self._update_dag_graph_for_dag(db, dag_id, graph)
            logger.info(f"Edge {from_task_id}->{to_task_id} added to DAG {dag_id}")
            return DagAdjacencyList(dag_id=dag_id, adjacency_list=graph)

    async def delete_edge(
        self,
        db: AsyncSession,
        dag_id: uuid.UUID,
        from_task_id: uuid.UUID,
        to_task_id: uuid.UUID,
    ) -> DagAdjacencyList:
        async with db.begin():
            await db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
            await db.execute(text("LOCK TABLE dag IN EXCLUSIVE MODE"))
            graph = await self._get_adjacency_list_for_dag(db, dag_id)
            if from_task_id in graph and to_task_id in graph[from_task_id]:
                graph[from_task_id].remove(to_task_id)
            await db.execute(
                delete(DagSchema).where(
                    DagSchema.dag_id == dag_id,
                    DagSchema.from_task_id == from_task_id,
                    DagSchema.to_task_id == to_task_id,
                )
            )
            await self._update_dag_graph_for_dag(db, dag_id, graph)
            logger.info(f"Edge {from_task_id}->{to_task_id} deleted from DAG {dag_id}")
            return DagAdjacencyList(dag_id=dag_id, adjacency_list=graph)

    async def create_dag(self, db: AsyncSession, dag_id: uuid.UUID):
        async with db.begin():
            await db.execute(
                update(text("dags"))
                .where(text("id = :id"))
                .params(id=str(dag_id))
                .values(dag_graph=json.dumps({}))
            )
            logger.info(f"DAG {dag_id} created with empty adjacency list")

    async def _get_adjacency_list_for_dag(self, db: AsyncSession, dag_id: uuid.UUID):
        result = await db.execute(select(DagSchema).where(DagSchema.dag_id == dag_id))
        edges = result.fetchall()
        graph = {}
        for edge in edges:
            f, t = edge.from_task_id, edge.to_task_id
            graph.setdefault(f, [])
            graph[f].append(t)
            if t not in graph:
                graph[t] = []
        return graph

    async def _update_dag_graph_for_dag(
        self, db: AsyncSession, dag_id: uuid.UUID, graph: dict
    ):
        graph_str = {str(k): [str(v) for v in vs] for k, vs in graph.items()}
        await db.execute(
            update(text("dags"))
            .where(text("id = :id"))
            .params(id=str(dag_id))
            .values(dag_graph=json.dumps(graph_str))
        )

    def _creates_cycle_in_memory(self, graph, from_id):
        visited = set()
        stack = set()

        def visit(node):
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for neighbor in graph.get(node, []):
                if visit(neighbor):
                    return True
            stack.remove(node)
            return False

        return visit(from_id)

    async def get_full_dag(self, db: AsyncSession, dag_id: uuid.UUID) -> dag:
        result = await db.execute(
            text("SELECT id, team_id, dag_graph FROM dags WHERE id = :id"),
            {"id": str(dag_id)},
        )
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="DAG not found")
        dag_id, team_id, dag_graph_json = row
        dag_graph = {
            uuid.UUID(k): [uuid.UUID(v) for v in vs]
            for k, vs in (json.loads(dag_graph_json) if dag_graph_json else {}).items()
        }

        task_ids = set()
        for from_id, to_ids in dag_graph.items():
            task_ids.add(from_id)
            task_ids.update(to_ids)
        task_ids = list(task_ids)

        tasks_repo = TasksRepository()
        tasks = await tasks_repo.get_tasks_by_ids(db, task_ids)
        task_objs = [TaskModel.from_orm(t) for t in tasks]

        return dag(
            dag_id=dag_id,
            team_id=team_id,
            DagAdjacencyList=DagAdjacencyList(dag_id=dag_id, adjacency_list=dag_graph),
            tasks=task_objs,
        )
