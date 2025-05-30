from app.core.repository.task_repository import TasksRepository
from app.core.repository.user_tasks_repository import UserTasksRepository
from app.core.repository.week_repository import WeekRepository
from app.schema.repository.week import week
from app.services.llm_service import LLMService
import uuid


async def analyze_and_create_week(db, start_of_week, end_of_week, user_id):
    tasks_repo = TasksRepository()
    user_tasks_repo = UserTasksRepository()

    # Find missed deadlines
    missed_deadlines = []
    # Get all tasks for user
    all_tasks = await tasks_repo.get_tasks_by_user(db, user_id)
    for t in all_tasks:
        # Unfinished and deadline before end of week
        if not t.date_of_completion and t.deadline and t.deadline < end_of_week:
            missed_deadlines.append(t.id)
        # Finished after start of week but after their due date
        elif (
            t.date_of_completion
            and t.date_of_completion > start_of_week
            and t.deadline
            and t.date_of_completion > t.deadline
        ):
            missed_deadlines.append(t.id)

    # Find collaborators
    collaborators = set()
    for t in all_tasks:
        # If not completed or completed in this week
        if (not t.date_of_completion) or (
            t.date_of_completion and start_of_week < t.date_of_completion < end_of_week
        ):
            user_ids = await user_tasks_repo.get_user_ids_for_task(db, t.id)
            for uid in user_ids:
                if uid != user_id:
                    collaborators.add(uid)

    # AI agentic function (placeholder)
    summary = "summary and feedback"
    feedback = "summary and feedback"

    # Completed tasks and points
    completed_tasks = []
    points_completed = 0
    completed = await tasks_repo.get_completed_tasks_for_user_in_range(
        db, user_id, start_of_week, end_of_week
    )
    for t in completed:
        completed_tasks.append(t.id)
        if t.points:
            points_completed += t.points

    week_obj = week(
        id=uuid.uuid4(),
        start_date=start_of_week,
        end_date=end_of_week,
        user_id=user_id,
        summary=summary,
        feedback=feedback,
        collaborators=list(collaborators) if collaborators else [],
        missed_deadlines=missed_deadlines,
        completed_tasks=completed_tasks,
        points_completed=points_completed,
    )
    # Create in DB
    return await encode_and_store([week_obj], db)


async def encode_and_store(weeks: list[week], db):
    """
    Takes a list of week Pydantic models, encodes each to a 1024 vector, and returns a list of (week, vector) tuples.
    """
    week_repo = WeekRepository()
    result = []
    for w in weeks:
        text_to_encode = " ".join(
            filter(
                None,
                [
                    w.summary or "",
                    w.feedback or "",
                    f"Completed {len(w.completed_tasks or [])} tasks",
                    f"Missed {len(w.missed_deadlines or [])} deadlines",
                    f"Earned {w.points_completed or 0} points",
                ],
            )
        )
        embedding = LLMService.encode_1024(text_to_encode)
        result.append((w, embedding))

    for vector_week in result:
        await week_repo.store_week(db, vector_week)
