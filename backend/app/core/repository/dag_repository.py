from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schema.repository.dag import DagSchema, dag
from app.core.logger import logger
import uuid
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass


@dataclass
class EdgeOperationResult:
    dag_id: uuid.UUID
    new_dag_id: Optional[uuid.UUID] = None


class DagRepository:
    def __init__(self):
        self.model = DagSchema

    def _find_connected_nodes(self, graph: Dict[str, List[str]], start_node: str) -> Set[str]:
        """Find all nodes connected to start_node in the graph."""
        visited = set()
        to_visit = {start_node}
        
        while to_visit:
            current = to_visit.pop()
            if current not in visited:
                visited.add(current)
                to_visit.update(graph.get(current, []))
        
        return visited

    def _split_graph(self, graph: Dict[str, List[str]], first: str, second: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """Split the graph into two parts when removing an edge."""
        # Remove the edge
        if first in graph and second in graph[first]:
            graph[first].remove(second)
        
        # Find all nodes connected to first node
        first_connected = self._find_connected_nodes(graph, first)
        
        # Create two new graphs
        first_graph = {k: [v for v in graph[k] if v in first_connected] 
                      for k in first_connected if k in graph}
        second_graph = {k: [v for v in graph[k] if v not in first_connected] 
                       for k in graph if k not in first_connected}
        
        return first_graph, second_graph

    def _merge_graphs(self, graph1: Dict[str, List[str]], graph2: Dict[str, List[str]], 
                     first: str, second: str) -> Dict[str, List[str]]:
        """Merge two graphs by adding an edge."""
        merged = graph1.copy()
        merged.update(graph2)
        
        # Add the new edge
        if first not in merged:
            merged[first] = []
        if second not in merged:
            merged[second] = []
        if second not in merged[first]:
            merged[first].append(second)
        
        return merged

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
            return dag(dag_id=obj.dag_id, team_id=obj.team_id, dag_graph=obj.dag_graph)
        except Exception as e:
            logger.error(f"Error fetching DAG {dag_id}: {e}")
            raise

    async def create_dag(
        self,
        db: AsyncSession,
        first_task_id: uuid.UUID,
        second_task_id: uuid.UUID,
        team_id: uuid.UUID,
    ) -> dag:
        try:
            dag_graph = {
                str(first_task_id): [str(second_task_id)],
                str(second_task_id): [],
            }
            new_dag = DagSchema(team_id=team_id, dag_graph=dag_graph)
            db.add(new_dag)
            await db.commit()
            await db.refresh(new_dag)
            logger.info(
                f"Created DAG {new_dag.dag_id} with edge {first_task_id} -> {second_task_id}"
            )
            return dag(dag_id=new_dag.dag_id, team_id=new_dag.team_id, dag_graph=dag_graph)
        except Exception as e:
            logger.error(f"Error creating DAG: {e}")
            raise

    async def add_edge(
        self,
        db: AsyncSession,
        dag_id: uuid.UUID,
        first_task_id: uuid.UUID,
        second_task_id: uuid.UUID,
    ) -> EdgeOperationResult:
        try:
            # Find the DAG containing second_task_id
            result = await db.execute(
                select(DagSchema).where(
                    DagSchema.dag_graph.cast(str).contains(str(second_task_id))
                )
            )
            second_dag = result.scalar_one_or_none()
            
            if second_dag and second_dag.dag_id != dag_id:
                # We need to merge two DAGs
                first_dag = await self.get_dag(db, dag_id)
                merged_graph = self._merge_graphs(
                    first_dag.dag_graph,
                    second_dag.dag_graph,
                    str(first_task_id),
                    str(second_task_id)
                )
                
                # Update the first DAG with the merged graph
                await db.execute(
                    update(DagSchema)
                    .where(DagSchema.dag_id == dag_id)
                    .values(dag_graph=merged_graph)
                )
                
                # Delete the second DAG
                await db.delete(second_dag)
                await db.commit()
                
                logger.info(f"Merged DAGs {dag_id} and {second_dag.dag_id}")
                return EdgeOperationResult(dag_id=dag_id, new_dag_id=None)
            else:
                # Just add the edge to the existing DAG
                result = await db.execute(
                    select(DagSchema).where(DagSchema.dag_id == dag_id)
                )
                obj = result.scalar_one_or_none()
                if not obj:
                    raise HTTPException(status_code=404, detail="DAG not found")
                
                dag_graph = obj.dag_graph
                first = str(first_task_id)
                second = str(second_task_id)
                
                if first not in dag_graph:
                    dag_graph[first] = []
                if second not in dag_graph:
                    dag_graph[second] = []
                if second not in dag_graph[first]:
                    dag_graph[first].append(second)
                
                await db.execute(
                    update(DagSchema)
                    .where(DagSchema.dag_id == dag_id)
                    .values(dag_graph=dag_graph)
                )
                await db.commit()
                
                logger.info(f"Added edge {first_task_id} -> {second_task_id} to DAG {dag_id}")
                return EdgeOperationResult(dag_id=dag_id)
        except Exception as e:
            logger.error(f"Error adding edge: {e}")
            raise

    async def delete_edge(
        self,
        db: AsyncSession,
        dag_id: uuid.UUID,
        first_task_id: uuid.UUID,
        second_task_id: uuid.UUID,
    ) -> EdgeOperationResult:
        try:
            result = await db.execute(
                select(DagSchema).where(DagSchema.dag_id == dag_id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(status_code=404, detail="DAG not found")
            
            dag_graph = obj.dag_graph
            first = str(first_task_id)
            second = str(second_task_id)
            
            # Split the graph
            first_graph, second_graph = self._split_graph(dag_graph, first, second)
            
            # Update the original DAG with the first part
            await db.execute(
                update(DagSchema)
                .where(DagSchema.dag_id == dag_id)
                .values(dag_graph=first_graph)
            )
            
            # If there's a second part, create a new DAG
            new_dag_id = None
            if second_graph:
                new_dag = DagSchema(team_id=obj.team_id, dag_graph=second_graph)
                db.add(new_dag)
                await db.commit()
                await db.refresh(new_dag)
                new_dag_id = new_dag.dag_id
                logger.info(f"Created new DAG {new_dag_id} after splitting")
            
            await db.commit()
            logger.info(f"Deleted edge {first_task_id} -> {second_task_id} from DAG {dag_id}")
            return EdgeOperationResult(dag_id=dag_id, new_dag_id=new_dag_id)
        except Exception as e:
            logger.error(f"Error deleting edge: {e}")
            raise

    async def get_dags_by_team(self, db: AsyncSession, team_id: uuid.UUID):
        try:
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
            logger.error(f"Error fetching DAGs for team {team_id}: {e}")
            raise

    async def get_all_dags(self, db: AsyncSession) -> List[dag]:
        try:
            result = await db.execute(select(DagSchema))
            objs = result.scalars().all()
            dags = []
            for obj in objs:
                dags.append(
                    dag(dag_id=obj.dag_id, team_id=obj.team_id, dag_graph=obj.dag_graph)
                )
            return dags
        except Exception as e:
            logger.error(f"Error fetching all DAGs: {e}")
            raise

