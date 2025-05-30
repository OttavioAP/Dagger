from uuid import uuid4
from app.core.agentic.agent_functions.base_agent_function import BaseAgentFunction
from app.services.llm_service import LLMService
from app.core.logger import logger
import json
import base64
from typing import Dict, Any, List, Callable
from app.schema.langgraph.week_state import WeekState
from app.core.agentic.agent_prompts.week_analysis_prompts import WeekAnalysisPrompts
from app.services.llm_service import Message


class WeekAnalysisFunctions(BaseAgentFunction):
    def add_mappings(self):
        return {
            self.create_summary_key(): self.create_summary_function,
            self.create_feedback_key(): self.create_feedback_function,
        }

    @staticmethod
    async def create_summary_function(state: WeekState) -> WeekState:
        prompt = Message(
            role="user",
            content=WeekAnalysisPrompts.create_summary_prompt(state),
        )
        llm_service = LLMService()

        response = await llm_service.query_llm(prompt, json_response=False)
        logger.info(
            "Response summary:"
            + (response.content if hasattr(response, "content") else str(response))
        )

        # Create new state with updated week summary
        new_week = state.week.copy()
        new_week.summary = (
            response.content if hasattr(response, "content") else str(response)
        )

        return WeekState(
            user=state.user, team=state.team, week=new_week, tasks=state.tasks
        )

    @staticmethod
    async def create_feedback_function(state: WeekState) -> WeekState:
        prompt = Message(
            role="user",
            content=WeekAnalysisPrompts.create_feedback_prompt(state),
        )

        llm_service = LLMService()

        response = await llm_service.query_llm(prompt, json_response=False)
        logger.info(
            "Response feedback:"
            + (response.content if hasattr(response, "content") else str(response))
        )

        # Create new state with updated week feedback
        new_week = state.week.copy()
        new_week.feedback = (
            response.content if hasattr(response, "content") else str(response)
        )

        return WeekState(
            user=state.user, team=state.team, week=new_week, tasks=state.tasks
        )

    @staticmethod
    def create_summary_key():
        return WeekAnalysisFunctions.create_summary_function.__name__

    @staticmethod
    def create_feedback_key():
        return WeekAnalysisFunctions.create_feedback_function.__name__
