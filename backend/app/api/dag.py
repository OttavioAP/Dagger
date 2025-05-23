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

router = APIRouter(prefix="/dag", tags=["dag"])
dag_repository = DagRepository()
tasks_repository = TasksRepository()


class DagAction(str, Enum):
    create = "create"
    add_edge = "add_edge"
    delete_edge = "delete_edge"


class DagRequest(BaseModel):
    dag_id: uuid.UUID
    first_task_id: uuid.UUID
    second_task_id: uuid.UUID = None
    action: DagAction


@router.post("/", response_model=DagModel, status_code=200)
async def dag_action(request: DagRequest, db: AsyncSession = Depends(get_db)):
    try:
        if request.action == DagAction.create:
            if request.first_task_id and request.second_task_id:
                await dag_repository.create_dag(
                    db, request.dag_id, request.first_task_id, request.second_task_id
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="first_task_id and second_task_id required for create",
                )
            logger.info(f"DAG {request.dag_id} created via API")
        elif request.action == DagAction.add_edge:
            if not request.second_task_id:
                raise HTTPException(
                    status_code=400, detail="second_task_id required for add_edge"
                )
            await dag_repository.add_edge(
                db, request.dag_id, request.first_task_id, request.second_task_id
            )
        elif request.action == DagAction.delete_edge:
            if not request.second_task_id:
                raise HTTPException(
                    status_code=400, detail="second_task_id required for delete_edge"
                )
            await dag_repository.delete_edge(
                db, request.dag_id, request.first_task_id, request.second_task_id
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        return await dag_repository.get_full_dag(db, request.dag_id)
    except Exception as e:
        logger.error(f"DAG API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by_team", response_model=List[DagModel])
async def get_dags_by_team(team_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await dag_repository.get_dags_by_team(db, team_id)
    except Exception as e:
        logger.error(f"Error in get_dags_by_team: {e}")
        raise HTTPException(status_code=500, detail=str(e))
