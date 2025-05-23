from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database_service import get_db
from app.core.repository.user_tasks_repository import UserTasksRepository
from app.schema.repository.user_tasks import user_tasks
from pydantic import BaseModel
from typing import Optional
from enum import Enum

router = APIRouter(prefix="/user_tasks", tags=["user_tasks"])
user_tasks_repository = UserTasksRepository()


class option(str, Enum):
    ADD = "add"
    DELETE = "delete"


class UserTasksRequest(BaseModel):
    user_id: str
    task_id: str
    action: option


@router.post("/", response_model=user_tasks, status_code=201)
async def modify_user_task(
    request: UserTasksRequest, db: AsyncSession = Depends(get_db)
):
    try:
        if request.action == option.ADD:
            new_user_task = user_tasks(
                user_id=request.user_id,
                task_id=request.task_id,
            )
            return await user_tasks_repository.add_user_task(db, new_user_task)
        elif request.action == option.DELETE:
            return await user_tasks_repository.delete_user_task(
                db, request.user_id, request.task_id
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[user_tasks])
async def get_all_user_tasks(db: AsyncSession = Depends(get_db)):
    try:
        return await user_tasks_repository.get_all_user_tasks(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
