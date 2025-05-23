from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.services.database_service import get_db
from app.core.repository.team_repository import TeamRepository
from app.schema.repository.team import team
from pydantic import BaseModel
from app.schema.repository.user import user
from app.schema.repository.user_teams import user_teams
from app.core.handlers.user_team_handler import UserTeamHandler

router = APIRouter(prefix="/teams", tags=["teams"])
team_repository = TeamRepository()


class CreateTeamRequest(BaseModel):
    team_name: str


@router.post("/", response_model=team, status_code=201)
async def create_team(request: CreateTeamRequest, db: AsyncSession = Depends(get_db)):
    try:
        new_team = team(team_name=request.team_name, id=uuid.uuid4())
        return await team_repository.create_team(db, new_team)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{team_id}", status_code=204)
async def delete_team(team_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await team_repository.delete_team(db, team_id)
        return {"detail": "Team deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class team_data(BaseModel):
    teams: list[team]
    users: list[user]
    user_teams: list[user_teams]


@router.get("/", response_model=list[team_data])
async def get_all_team_data(db: AsyncSession = Depends(get_db)):
    try:
        return await UserTeamHandler.get_all_team_data(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
