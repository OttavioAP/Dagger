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
import json
from pathlib import Path
from app.services.week_service import encode_and_store

router = APIRouter(prefix="/week", tags=["week"])
week_repository = WeekRepository()


class WeekRequestType(str, Enum):
    SEARCH_QUERY = "search_query"
    COMPARE_WEEKS = "compare_weeks"
    GET_WEEKS = "get_weeks"


class WeekResponse(BaseModel):
    weeks: List[week]
    total_count: int


@router.get("/", response_model=WeekResponse)
async def get_weeks(
    request_type: WeekRequestType = Query(...),
    query: Optional[str] = None,
    week_id: Optional[uuid.UUID] = None,
    number_of_weeks: int = Query(...),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[uuid.UUID] = None,
    team_id: Optional[uuid.UUID] = None,
    collaborators: Optional[List[uuid.UUID]] = Query(None),
    missed_deadlines_range: Optional[Tuple[int, int]] = Query(None),
    completed_task_range: Optional[Tuple[int, int]] = Query(None),
    points_range: Optional[Tuple[int, int]] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        if request_type == WeekRequestType.GET_WEEKS:
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
                points_range=points_range,
            )
            return WeekResponse(weeks=weeks, total_count=len(weeks))

        elif request_type == WeekRequestType.COMPARE_WEEKS:
            if not week_id:
                raise HTTPException(
                    status_code=400, detail="week_id is required for compare_weeks"
                )

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
                points_range=points_range,
            )
            return WeekResponse(weeks=weeks, total_count=len(weeks))

        elif request_type == WeekRequestType.SEARCH_QUERY:
            if not query:
                raise HTTPException(
                    status_code=400, detail="query is required for search_query"
                )

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
                points_range=points_range,
            )
            return WeekResponse(weeks=weeks, total_count=len(weeks))

        else:
            raise HTTPException(status_code=400, detail="Invalid request type")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-weeks-from-json")
async def import_weeks_from_json(db: AsyncSession = Depends(get_db)):
    try:
        """
        Import all weeks from weeks.json, parse as week Pydantic models, encode, and store each.
        """
        weeks_path = Path("/home/argos/Dagger/db/example_data/weeks.json")
        if not weeks_path.exists():
            raise HTTPException(status_code=404, detail="weeks.json not found")
        with weeks_path.open() as f:
            data = json.load(f)
        weeks_raw = data.get("weeks", [])
        week_objs = []
        for week_dict in weeks_raw:
            # Parse UUIDs in collaborators, missed_deadlines, completed_tasks
            for key in ["collaborators", "missed_deadlines", "completed_tasks"]:
                if week_dict.get(key) is not None:
                    week_dict[key] = [uuid.UUID(x) for x in week_dict[key]]
            # Parse user_id and id
            if week_dict.get("user_id"):
                week_dict["user_id"] = uuid.UUID(week_dict["user_id"])
            if week_dict.get("id"):
                week_dict["id"] = uuid.UUID(week_dict["id"])
            week_objs.append(week(**week_dict))
        # Encode all weeks and get (week, vector) tuples
        return await encode_and_store(week_objs, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
