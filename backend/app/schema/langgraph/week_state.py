from pydantic import BaseModel
from app.schema.repository.week import week
from app.schema.repository.user import user
from app.schema.repository.team import team
from app.schema.repository.tasks import task
from typing import List

class WeekState(BaseModel):
    user: user
    team: team
    week: week
    tasks: List[task]
