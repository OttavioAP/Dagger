from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from app.services.database_service import get_db
from app.core.repository.user_repository import UserRepository
from app.schema.repository.user import user
from pydantic import BaseModel
from enum import Enum
from typing import Optional
router = APIRouter(prefix="/user", tags=["user"])
user_repository = UserRepository()


class UpdateUserOption(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class UpdateUserRequest(BaseModel):
    user_id: uuid.UUID
    team_id: Optional[uuid.UUID] = None
    action: UpdateUserOption


@router.post("/", response_model=user, status_code=201)
async def update_user(request: UpdateUserRequest, db: AsyncSession = Depends(get_db)):
    try:
        if request.action == UpdateUserOption.CREATE:
            # For create, we need to create a new user with the provided ID and team_id
            new_user = user(id=request.user_id, team_id=request.team_id)
            return await user_repository.create_user(db, new_user)
        elif request.action == UpdateUserOption.UPDATE:
            # For update, we need to get the existing user and update its team_id
            existing_user = await user_repository.get_user(db, str(request.user_id))
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")
            existing_user.team_id = request.team_id
            return await user_repository.update_user(db, existing_user)
        elif request.action == UpdateUserOption.DELETE:
            return await user_repository.delete_user(db, str(request.user_id))
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_user_by_username", response_model=user)
async def get_user_by_username(username: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        result = await user_repository.get_by_username(db, username)
        if result is None:
            new_user = await user_repository.create_user(
                db, user(username=username, id=uuid.uuid4())
            )
            #cheating here to avoid creating real auth
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
