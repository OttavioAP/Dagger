from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.services.database_service import get_db
from app.core.repository.week_repository import WeekRepository
from app.schema.repository.week import week

router = APIRouter(prefix="/week", tags=["week"])
week_repository = WeekRepository()


@router.get("/", response_model=List[week])
async def get_weeks(
    user_id: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await week_repository.get_weeks(db, user_id=user_id, team_id=team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
