from app.schema.llm.tool import (
    AbstractTool,
    ToolSchema,
    ToolFunction,
    ToolFunctionParameters,
    ToolParameterProperty,
)
from typing import Callable, ClassVar, Optional, List, Tuple
from datetime import datetime
import uuid
from app.core.repository.week_repository import WeekRepository
from app.schema.repository.week import week
from app.core.logger import logger
from app.core.repository.user_repository import UserRepository


class SearchWeeksTool(AbstractTool):
    """Tool for searching weeks using semantic search and metadata filters. Use this to get context about a users past work."""

    tool_schema: ClassVar[ToolSchema] = ToolSchema(
        type="function",
        function=ToolFunction(
            name="SearchWeeksTool",
            description="Search weeks using semantic search and metadata filters. Returns a list of week summaries. Use this to get context about a users past work.",
            parameters=ToolFunctionParameters(
                type="object",
                properties={
                    "query": ToolParameterProperty(
                        type="string",
                        description="The semantic search query string. You can use the users question directly, or rephrase it to make it more specific.",
                    ),
                    "number_of_weeks": ToolParameterProperty(
                        type="integer",
                        description="Number of weeks to return.",
                        minimum=1,
                        maximum=100,
                        default=5,
                    ),
                    "start_date": ToolParameterProperty(
                        type="string",
                        description="The start date (ISO 8601 format) for filtering weeks.",
                        default=None,
                    ),
                    "end_date": ToolParameterProperty(
                        type="string",
                        description="The end date (ISO 8601 format) for filtering weeks.",
                        default=None,
                    ),
                    "user_id": ToolParameterProperty(
                        type="string",
                        description="The user ID (UUID) to filter weeks.",
                    ),
                    "collaborators": ToolParameterProperty(
                        type="array",
                        description="List of collaborator usernames.",
                        items={"type": "string"},
                        default=None,
                    ),
                    "missed_deadlines_range": ToolParameterProperty(
                        type="array",
                        description="Tuple [min, max] for missed deadlines count.",
                        items={"type": "integer"},
                        default=None,
                    ),
                    "completed_task_range": ToolParameterProperty(
                        type="array",
                        description="Tuple [min, max] for completed tasks count.",
                        items={"type": "integer"},
                        default=None,
                    ),
                    "points_range": ToolParameterProperty(
                        type="array",
                        description="Tuple [min, max] for points completed.",
                        items={"type": "integer"},
                        default=None,
                    ),
                },
                required=["query", "user_id"],
            ),
        ),
    )

    @classmethod
    def tool_function(cls) -> Callable:
        return cls.search_weeks

    @classmethod
    async def search_weeks(
        cls,
        query: str,
        user_id: str,
        number_of_weeks: int = 5,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        collaborators: Optional[List[str]] = None,  # usernames
        missed_deadlines_range: Optional[List[int]] = None,
        completed_task_range: Optional[List[int]] = None,
        points_range: Optional[List[int]] = None,
        db=None,  # db session should be injected by the caller
    ) -> List[week]:
        """
        Search weeks using semantic search and metadata filters. user_id is required. number_of_weeks is optional and defaults to 5. Collaborators is a list of usernames.
        """
        try:
            repo = WeekRepository()
            user_repo = UserRepository()
            # Convert string dates to datetime
            start_dt = datetime.fromisoformat(start_date) if start_date else None
            end_dt = datetime.fromisoformat(end_date) if end_date else None
            # Convert string UUIDs to UUID objects
            user_uuid = uuid.UUID(user_id)
            # Convert collaborator usernames to UUIDs
            collaborators_uuids = None
            if collaborators:
                collaborators_uuids = []
                for username in collaborators:
                    user_obj = await user_repo.get_by_username(db, username)
                    if user_obj and hasattr(user_obj, "id"):
                        collaborators_uuids.append(user_obj.id)
                        logger.info(
                            f"Resolved collaborator username '{username}' to id '{user_obj.id}'"
                        )
                    else:
                        logger.warning(
                            f"Could not resolve collaborator username '{username}' to a user id"
                        )
            # Convert ranges
            missed_range = (
                tuple(missed_deadlines_range) if missed_deadlines_range else None
            )
            completed_range = (
                tuple(completed_task_range) if completed_task_range else None
            )
            points_rng = tuple(points_range) if points_range else None
            # Call the repository method
            results = await repo.search_weeks(
                db=db,
                query=query,
                user_id=user_uuid,
                number_of_weeks=number_of_weeks,
                start_date=start_dt,
                end_date=end_dt,
                collaborators=collaborators_uuids,
                missed_deadlines_range=missed_range,
                completed_task_range=completed_range,
                points_range=points_rng,
            )
            return results
        except Exception as e:
            logger.error(f"Exception in SearchWeeksTool.search_weeks: {e}")
            raise
