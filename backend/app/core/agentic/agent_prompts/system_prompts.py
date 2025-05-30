from app.core.repository.user_repository import UserRepository
from app.core.repository.team_repository import TeamRepository
from app.core.repository.user_tasks_repository import UserTasksRepository
from app.core.repository.task_repository import TasksRepository
from app.schema.repository.user import user as UserModel
from app.schema.repository.team import team as TeamModel
from app.schema.repository.tasks import task as TaskModel
from app.schema.repository.user_tasks import user_tasks as UserTasksModel
from fastapi import HTTPException
from datetime import datetime


def get_class_attributes_docstrings(cls):
    """Get all attributes and their docstrings from a class."""
    attributes = []
    for name, field in getattr(cls, "model_fields", {}).items():
        if name != "id":  # Skip the id field as it's not relevant for the prompt
            doc = (
                getattr(field, "description", None)
                or getattr(field.annotation, "__doc__", None)
                or "No description available"
            )
            attributes.append(f"- {name}: {doc}")
    return "\n".join(attributes)


class SystemPrompts:
    @staticmethod
    async def chat_system_system_prompt(db, username: str):
        """
        Returns the system prompt for the AI chatbot, dynamically filled with user, team, and task context.
        """
        try:
            # User context
            user_repo = UserRepository()
            user_obj = await user_repo.get_by_username(db, username)
            if user_obj is None:
                raise ValueError(f"User '{username}' not found.")
            user_context = (
                f"{UserModel.__doc__.strip()}\n"
                f"Username: {user_obj.username}\n"
                f"User ID: {user_obj.id}\n"
                f"Team ID: {user_obj.team_id}\n"
                f"User attributes:\n{get_class_attributes_docstrings(UserModel)}"
            )

            # Team context
            team_repo = TeamRepository()
            team_obj = await team_repo.get_team_by_user_id(db, str(user_obj.id))
            if team_obj is None:
                team_context = "User is not assigned to any team."
            else:
                team_members = await user_repo.get_users_by_team(db, str(team_obj.id))
                member_names = ", ".join([u.username for u in team_members])
                team_context = (
                    f"{TeamModel.__doc__.strip()}\n"
                    f"Team name: {team_obj.team_name}\n"
                    f"Team ID: {team_obj.id}\n"
                    f"Team members: {member_names}\n"
                    f"Team attributes:\n{get_class_attributes_docstrings(TeamModel)}"
                )

            # User's current tasks
            user_tasks_repo = UserTasksRepository()
            task_repo = TasksRepository()
            task_ids = await user_tasks_repo.get_task_ids_for_user(db, str(user_obj.id))
            tasks = await task_repo.get_tasks_by_ids(db, task_ids)
            # Filter for tasks with no completion date
            incomplete_tasks = [
                t for t in tasks if getattr(t, "date_of_completion", None) is None
            ]
            if incomplete_tasks:
                tasks_context = f"{TaskModel.__doc__.strip()}\n" + "\n".join(
                    [f"- {t.task_name}: {t.description}" for t in incomplete_tasks]
                )
            else:
                tasks_context = "No current (incomplete) tasks."

            # UserTasks attributes
            user_tasks_attributes = get_class_attributes_docstrings(UserTasksModel)

            # Compose the system prompt
            prompt = (
                "You are a helpful AI chatbot who enhances the productivity for office workers. You are compliant, and willing to help them with any work related task or question. When given a task you don't know how to do, give your best effort. When you respond to users, you only provide human readable information, not uuids.\n\n"
                f"The user you're assisting is:\n{user_context}\n\n"
                f"Their team is:\n{team_context}\n\n"
                f"The user's current tasks are:\n{tasks_context}\n\n"
                f"User-task assignment attributes (user_tasks):\n{user_tasks_attributes}"
                f"It is currently {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return prompt
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
