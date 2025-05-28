from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional, Tuple
from pydantic import BaseModel
from app.schema.repository.week import week
from app.core.repository.week_repository import WeekRepository
from app.services.database_service import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/agentic", tags=["agentic"])
week_repository = WeekRepository()

class SearchType(str, Enum):
    REGULAR = "regular"
    SEMANTIC = "semantic"
    COMPARE = "compare"

class SearchResponse(BaseModel):
    reply: str
    weeks: List[week]
    total_count: int

@router.get("/search", response_model=SearchResponse)
async def agentic_search(
    search_type: SearchType = Query(...),
    query: Optional[str] = None,
    week_id: Optional[uuid.UUID] = None,
    number_of_weeks: int = Query(default=5),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[uuid.UUID] = None,
    team_id: Optional[uuid.UUID] = None,
    collaborators: Optional[List[uuid.UUID]] = Query(None),
    missed_deadlines_range: Optional[Tuple[int, int]] = Query(None),
    completed_task_range: Optional[Tuple[int, int]] = Query(None),
    points_range: Optional[Tuple[int, int]] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        if search_type == SearchType.REGULAR:
            if not query:
                raise HTTPException(status_code=400, detail="query is required for regular search")
            
            weeks = await week_repository.non_semantic_week_search(
                db=db,
                number_of_weeks=number_of_weeks,
                start_date=start_date,
                end_date=end_date,
                user_id=user_id,
                team_id=team_id,
                collaborators=collaborators,
                missed_deadlines_range=missed_deadlines_range,
                completed_task_range=completed_task_range,
                points_range=points_range
            )
            return SearchResponse(
                reply=f"Regular search results for query: {query}",
                weeks=weeks,
                total_count=len(weeks)
            )

        elif search_type == SearchType.SEMANTIC:
            if not query:
                raise HTTPException(status_code=400, detail="query is required for semantic search")
            
            weeks = await week_repository.search_weeks(
                db=db,
                query=query,
                number_of_weeks=number_of_weeks,
                start_date=start_date,
                end_date=end_date,
                user_id=user_id,
                collaborators=collaborators,
                missed_deadlines_range=missed_deadlines_range,
                completed_task_range=completed_task_range,
                points_range=points_range
            )
            return SearchResponse(
                reply=f"Semantic search results for query: {query}",
                weeks=weeks,
                total_count=len(weeks)
            )

        elif search_type == SearchType.COMPARE:
            if not week_id:
                raise HTTPException(status_code=400, detail="week_id is required for comparison search")
            
            # Get the vector of the reference week
            reference_week = await week_repository.get_by_id(db, week_id)
            if not reference_week:
                raise HTTPException(status_code=404, detail="Reference week not found")
            
            weeks = await week_repository.compare_weeks(
                db=db,
                vector=reference_week.embedding,
                number_of_weeks=number_of_weeks,
                start_date=start_date,
                end_date=end_date,
                user_id=user_id,
                collaborators=collaborators,
                missed_deadlines_range=missed_deadlines_range,
                completed_task_range=completed_task_range,
                points_range=points_range
            )
            return SearchResponse(
                reply=f"Comparison search results for week: {week_id}",
                weeks=weeks,
                total_count=len(weeks)
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid search type")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
