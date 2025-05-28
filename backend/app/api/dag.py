from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database_service import get_db
from app.core.repository.dag_repository import DagRepository
from app.core.repository.task_repository import TasksRepository
from app.schema.repository.tasks import task
from app.schema.repository.dag import dag as DagModel
from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from app.core.logger import logger
import uuid


class DagAction(str, Enum):
    add_edges = "add_edges"
    delete_edges = "delete_edges"


class DagRequest(BaseModel):
    first_task_id: uuid.UUID
    dependencies: List[uuid.UUID]
    team_id: uuid.UUID
    action: DagAction


class DagResponse(BaseModel):
    success: bool
    message: str


router = APIRouter(prefix="/dag", tags=["dag"])
dag_repository = DagRepository()
tasks_repository = TasksRepository()


@router.post("/", response_model=DagResponse, status_code=200)
async def dag_action(request: DagRequest, db: AsyncSession = Depends(get_db)):
    try:
        if request.action == DagAction.create:
            if request.first_task_id and request.second_task_id:
                dag = await dag_repository.create_dag(
                    db, request.first_task_id, request.second_task_id, request.team_id
                )
                return DagResponse(
                    success=True, message="DAG created successfully", dag_id=dag.dag_id
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="first_task_id and second_task_id required for create",
                )
        elif request.action == DagAction.add_edges:
            # Add multiple edges from first_task_id to each dependency
            result = await dag_repository.add_edges(
                db, request.first_task_id, request.dependencies, request.team_id
            )
            return DagResponse(
                success=True, message="Edges added successfully", **result
            )
        elif request.action == DagAction.delete_edges:
            # Remove multiple edges from first_task_id to each dependency
            result = await dag_repository.delete_edges(
                db, request.dag_id, request.first_task_id, request.dependencies
            )
            return DagResponse(
                success=True, message="Edges deleted successfully", **result
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
    except Exception as e:
        logger.error(f"DAG API error: {e}")
        return DagResponse(success=False, message=str(e))


@router.get("/", response_model=List[DagModel])
async def get_all_dags(db: AsyncSession = Depends(get_db)):
    try:
        return await dag_repository.get_all_dags(db)
    except Exception as e:
        logger.error(f"Error in get_all_dags: {e}")
        raise HTTPException(status_code=500, detail=str(e))
