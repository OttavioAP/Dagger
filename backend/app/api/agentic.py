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
from fastapi.responses import StreamingResponse
import time
from app.services.llm_service import LLMService
from app.schema.llm.message import Message
from app.core.tools.search_weeks_tool import SearchWeeksTool
from app.core.agentic.agent_prompts.system_prompts import SystemPrompts
from app.core.repository.user_repository import UserRepository

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


def generate_streamed_response(query: str):
    # Simulate a token stream (replace with real logic as needed)
    tokens = ["Hello", ",", " I", " am", " your", " chatbot", "."]
    for token in tokens:
        yield f"data: {token}\n\n"
        time.sleep(0.3)


@router.get("/chat")
async def chat(query: str, user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Chat endpoint that takes a string query and required user_id, calls the LLM with SearchWeeksTool, and returns the response string.
    """
    llm = LLMService()
    import json

    # Get username from user_id
    user_repo = UserRepository()
    user_obj = await user_repo.get_user(db, user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    username = user_obj.username

    # Get the system prompt
    system_prompt = await SystemPrompts.chat_system_system_prompt(db, username)

    user_message = Message(
        role="user", content=json.dumps({"query": query, "user_id": user_id})
    )
    # Call the LLM with the SearchWeeksTool available and system prompt injected
    response = await llm.query_llm(
        messages=[user_message], tools=["SearchWeeksTool"], system_prompt=system_prompt
    )
    # If the response is a Message object, return its content; if dict, return as string
    if hasattr(response, "content"):
        return {"response": response.content}
    return {"response": str(response)}
