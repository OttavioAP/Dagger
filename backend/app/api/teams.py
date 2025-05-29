from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.services.database_service import get_db
from app.core.repository.team_repository import TeamRepository
from app.schema.repository.team import team
from pydantic import BaseModel
from typing import List
from app.core.logger import logger

router = APIRouter(prefix="/teams", tags=["teams"])
team_repository = TeamRepository()


class CreateTeamRequest(BaseModel):
    team_name: str


@router.post("/", response_model=team, status_code=201)
async def create_team(request: CreateTeamRequest, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Received request to create team: {request.team_name}")
        new_team = team(team_name=request.team_name, id=uuid.uuid4())
        result = await team_repository.create_team(db, new_team)
        logger.info(f"Team created successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{team_id}", status_code=204)
async def delete_team(team_id: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Received request to delete team with id: {team_id}")
        await team_repository.delete_team(db, team_id)
        logger.info(f"Team deleted successfully: {team_id}")
        return {"detail": "Team deleted"}
    except Exception as e:
        logger.error(f"Error deleting team: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[team])
async def get_all_teams(db: AsyncSession = Depends(get_db)):
    try:
        logger.info("Received request to get all teams")
        teams = await team_repository.get_all_teams(db)
        logger.info(f"Fetched teams: {teams}")
        return teams
    except Exception as e:
        logger.error(f"Error fetching teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))
