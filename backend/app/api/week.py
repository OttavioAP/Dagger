from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.services.database_service import get_db
from app.core.repository.week_repository import WeekRepository
from app.schema.repository.week import week
import uuid
router = APIRouter(prefix="/week", tags=["week"])
week_repository = WeekRepository()


@router.get("/", response_model=List[week])
async def get_weeks(
    user_id: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        #return await week_repository.get_weeks(db, user_id=user_id, team_id=team_id)
        #return dummy week data for now
        #for loop to generate 10 dummy weeks
        dummyweeks = []
        for i in range(10):
            dummyweek = week(id=str(uuid.uuid4()), name="Week " + str(i+1), start_date="2024-01-01", end_date="2024-01-07", team_id="0411b0ba-6528-499f-a8b9-c91f4b8d7289", user_id=str(uuid.uuid4()), missed_deadlines=[], completed_tasks=[], points_completed=10)
            dummyweeks.append(dummyweek)
        return dummyweeks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
