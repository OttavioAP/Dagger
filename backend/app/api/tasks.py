from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.services.database_service import get_db
from app.core.repository.task_repository import TasksRepository
from app.schema.repository.tasks import task, TaskPriority, TaskFocus
from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from enum import Enum
from datetime import datetime
from app.core.logger import logger
router = APIRouter(prefix="/tasks", tags=["tasks"])


class task_action(str, Enum):
    create = "create"
    edit = "edit"
    delete = "delete"
    complete = "complete"


class TaskRequest(BaseModel):
    task_id: uuid.UUID | None = None
    task_name: str | None = None
    team_id: uuid.UUID | None = None
    deadline: datetime | None = None
    points: int | None = None
    priority: TaskPriority | None = TaskPriority.LOW
    focus: TaskFocus | None = TaskFocus.LOW
    description: str | None = None
    notes: str | None = None
    action: task_action


@router.post("/", response_model=task, status_code=201)
async def task_post(request: TaskRequest, db: AsyncSession = Depends(get_db)):
    try:
        tasks_repository = TasksRepository()
        logger.info(f"Received request: {request}")
        
        if request.action == task_action.create:
            # For create, we need task_name and team_id
            if not request.task_name or not request.team_id:
                raise HTTPException(status_code=400, detail="task_name and team_id are required for create")
            
            # Create task object with provided fields
            task_data = {
                "task_name": request.task_name,
                "team_id": request.team_id,
                "deadline": request.deadline,
                "points": request.points,
                "priority": request.priority or TaskPriority.LOW,
                "focus": request.focus or TaskFocus.LOW,
                "description": request.description,
                "notes": request.notes
            }
            return await tasks_repository.create_task(db, task_data)
            
        elif request.action == task_action.edit:
            # For edit, we need task_id
            if not request.task_id:
                raise HTTPException(status_code=400, detail="task_id is required for edit")
            
            # Create updates dict with non-None fields
            updates = {
                k: v for k, v in request.model_dump().items() 
                if v is not None and k not in ['action', 'task_id']
            }
            return await tasks_repository.edit_task(db, request.task_id, updates)
            
        elif request.action == task_action.delete:
            # For delete, we only need task_id
            if not request.task_id:
                raise HTTPException(status_code=400, detail="task_id is required for delete")
            return await tasks_repository.delete_task(db, request.task_id)

        elif request.action == task_action.complete:
            # For complete, we need task_id
            if not request.task_id:
                raise HTTPException(status_code=400, detail="task_id is required for complete")
            
            # Create updates dict with non-None fields and add current timestamp
            updates = {
                k: v for k, v in request.model_dump().items() 
                if v is not None and k not in ['action', 'task_id']
            }
            updates['date_of_completion'] = datetime.now()
            
            return await tasks_repository.edit_task(db, request.task_id, updates)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[task])
async def get_all_tasks(db: AsyncSession = Depends(get_db)):
    try:
        tasks_repository = TasksRepository()
        return await tasks_repository.get_all(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
