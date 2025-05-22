from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.services.database_service import get_db
from app.core.repository.task_repository import TasksRepository
from app.schema.repository.tasks import task
from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from enum import Enum

router = APIRouter(prefix="/tasks", tags=["tasks"])
tasks_repository = TasksRepository()


class task_action(str, Enum):
    create = "create"
    edit = "edit"
    delete = "delete"


class TaskRequest(BaseModel):
    task: task
    action: task_action


@router.post("/", response_model=task, status_code=201)
async def task_action(request: TaskRequest, db: AsyncSession = Depends(get_db)):
    try:
        # conditionally create, edit, or delete task
        if request.action == task_action.create:
            return await tasks_repository.create_task(db, request.task)
        elif request.action == task_action.edit:
            return await tasks_repository.edit_task(db, request.task)
        elif request.action == task_action.delete:
            return await tasks_repository.delete_task(db, request.task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}", response_model=list[task])
async def get_all_tasks_by_team(team_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await tasks_repository.get_all_tasks_by_team(db, team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
