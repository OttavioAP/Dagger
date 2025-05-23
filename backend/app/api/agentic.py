from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel
from app.schema.repository.week import week
import uuid

router = APIRouter(prefix="/agentic", tags=["agentic"])


class SearchResponse(BaseModel):
    reply: str
    weeks: List[week]


@router.get("/search", response_model=SearchResponse)
def agentic_search(
    query: str = Query(...),
    username: str = Query(...),
    team_name: str = Query(...),
):
    # Dummy data for now
    dummy_week = week(
        id=uuid.uuid4(),
        start_date="2024-06-03T00:00:00Z",
        end_date="2024-06-09T23:59:59Z",
        user_id=uuid.uuid4(),
        summary="Dummy summary",
        feedback="Dummy feedback",
        collaborators=[uuid.uuid4(), uuid.uuid4()],
        missed_deadlines=[uuid.uuid4()],
        completed_tasks=[uuid.uuid4()],
        points_completed=10,
    )
    return SearchResponse(
        reply=f"Query '{query}' for user '{username}' in team '{team_name}' processed.",
        weeks=[dummy_week],
    )
