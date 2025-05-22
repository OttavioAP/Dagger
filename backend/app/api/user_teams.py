from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.database_service import get_db
from app.core.repository.user_teams_repository import UserTeamsRepository
from app.schema.repository.user_teams import user_teams
from pydantic import BaseModel

router = APIRouter(prefix="/user_teams", tags=["user_teams"])
user_teams_repository = UserTeamsRepository()


class UserTeamsRequest(BaseModel):
    user_id: str
    team_id: str


@router.post("/", response_model=user_teams, status_code=201)
async def add_user_team(request: UserTeamsRequest, db: AsyncSession = Depends(get_db)):
    try:
        new_user_team = user_teams(user_id=request.user_id, team_id=request.team_id)
        return await user_teams_repository.add_user_team(db, new_user_team)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/", status_code=204)
async def delete_user_team(
    user_id: str, team_id: str, db: AsyncSession = Depends(get_db)
):
    try:
        await user_teams_repository.delete_user_team(db, user_id, team_id)
        return {"detail": "User-Team mapping deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[user_teams])
async def get_all_user_teams(db: AsyncSession = Depends(get_db)):
    try:
        return await user_teams_repository.get_all_user_teams(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
