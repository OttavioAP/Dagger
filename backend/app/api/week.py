from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.services.database_service import get_db
from app.core.repository.week_repository import WeekRepository
from app.schema.repository.week import week
from pydantic import BaseModel
from enum import Enum
import uuid
from datetime import datetime
from typing import Tuple

router = APIRouter(prefix="/week", tags=["week"])
week_repository = WeekRepository()

class WeekRequestType(str, Enum):
    SEARCH_QUERY = "search_query"
    COMPARE_WEEKS = "compare_weeks"
    GET_WEEKS = "get_weeks"

class WeekRequest(BaseModel):
    request_type: WeekRequestType
    query: Optional[str] = None
    week_id: Optional[uuid.UUID] = None
    number_of_weeks: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    collaborators: Optional[List[uuid.UUID]] = None
    missed_deadlines_range: Optional[Tuple[int, int]] = None
    completed_task_range: Optional[Tuple[int, int]] = None
    points_range: Optional[Tuple[int, int]] = None

class WeekResponse(BaseModel):
    weeks: List[week]
    total_count: int

@router.post("/", response_model=WeekResponse)
async def get_weeks(request: WeekRequest, db: AsyncSession = Depends(get_db)):
    try:
        if request.request_type == WeekRequestType.GET_WEEKS:
            weeks = await week_repository.non_semantic_week_search(
                db=db,
                number_of_weeks=request.number_of_weeks,
                start_date=request.start_date,
                end_date=request.end_date,
                user_id=request.user_id,
                team_id=request.team_id,
                collaborators=request.collaborators,
                missed_deadlines_range=request.missed_deadlines_range,
                completed_task_range=request.completed_task_range,
                points_range=request.points_range
            )
            return WeekResponse(weeks=weeks, total_count=len(weeks))

        elif request.request_type == WeekRequestType.COMPARE_WEEKS:
            if not request.week_id:
                raise HTTPException(status_code=400, detail="week_id is required for compare_weeks")
            
            # Get the vector of the reference week
            reference_week = await week_repository.get_by_id(db, request.week_id)
            if not reference_week:
                raise HTTPException(status_code=404, detail="Reference week not found")
            
            weeks = await week_repository.compare_weeks(
                db=db,
                vector=reference_week.embedding,
                number_of_weeks=request.number_of_weeks,
                start_date=request.start_date,
                end_date=request.end_date,
                user_id=request.user_id,
                collaborators=request.collaborators,
                missed_deadlines_range=request.missed_deadlines_range,
                completed_task_range=request.completed_task_range,
                points_range=request.points_range
            )
            return WeekResponse(weeks=weeks, total_count=len(weeks))

        elif request.request_type == WeekRequestType.SEARCH_QUERY:
            if not request.query:
                raise HTTPException(status_code=400, detail="query is required for search_query")
            
            weeks = await week_repository.search_weeks(
                db=db,
                query=request.query,
                number_of_weeks=request.number_of_weeks,
                start_date=request.start_date,
                end_date=request.end_date,
                user_id=request.user_id,
                collaborators=request.collaborators,
                missed_deadlines_range=request.missed_deadlines_range,
                completed_task_range=request.completed_task_range,
                points_range=request.points_range
            )
            return WeekResponse(weeks=weeks, total_count=len(weeks))

        else:
            raise HTTPException(status_code=400, detail="Invalid request type")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
