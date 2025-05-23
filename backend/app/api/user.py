from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from app.services.database_service import get_db
from app.core.repository.user_repository import UserRepository
from app.schema.repository.user import user
from pydantic import BaseModel
from enum import Enum

router = APIRouter(prefix="/user", tags=["user"])
user_repository = UserRepository()


class UpdateUserOption(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class UpdateUserRequest(BaseModel):
    user: user
    action: UpdateUserOption


@router.post("/", response_model=user, status_code=201)
async def update_user(request: UpdateUserRequest, db: AsyncSession = Depends(get_db)):
    try:
        if request.action == UpdateUserOption.CREATE:
            return await user_repository.create_user(db, request.user)
        elif request.action == UpdateUserOption.UPDATE:
            return await user_repository.update_user(db, request.user)
        elif request.action == UpdateUserOption.DELETE:
            return await user_repository.delete_user(db, request.user)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_user_by_username", response_model=user)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await user_repository.get_by_username(db, username)
        if result is None:
            new_user = await user_repository.create_user(
                db, user(username=username, id=uuid.uuid4())
            )
            return new_user
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by_team", response_model=List[user])
async def get_users_by_team(team_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await user_repository.get_users_by_team(db, team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
