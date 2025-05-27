from app.schema.langgraph.week_state import WeekState
from app.schema.repository.user import user
from app.schema.repository.team import team
from app.schema.repository.tasks import task
from app.schema.repository.week import week
import inspect

def get_class_attributes_docstrings(cls):
    """Get all attributes and their docstrings from a class."""
    attributes = []
    for name, field in cls.model_fields.items():
        if name != 'id':  # Skip the id field as it's not relevant for the prompt
            doc = field.description or field.annotation.__doc__ or "No description available"
            attributes.append(f"- {name}: {doc}")
    return "\n".join(attributes)

class WeekAnalysisPrompts:
    @staticmethod
    def create_summary_prompt(week_state: WeekState)->str: 
        return f"""
        You are a helpful assistant optimizing the productivity of an employee who has a certain set of tasks for the week. The employee is
        {week_state.user.username} (ID: {week_state.user.id}). {user.__doc__}
        The employee is part of a team, {week_state.team.team_name} (ID: {week_state.team.id}). {team.__doc__}
        The employee has a certain set of tasks for the week:
        {week_state.tasks}  # {task.__doc__}
        Each task contains:
        {get_class_attributes_docstrings(task)}
        The week you're analyzing is from {week_state.week.start_date} to {week_state.week.end_date}. {week.__doc__}
        This week includes:
        {get_class_attributes_docstrings(week)}

        The employee has asked you to create a summary of the week. The summary should be a lengthy description of the week's work. focus on the nature of the tasks,
        the challenges faced, tools and resources used, collaboration with other team members, the solutions found, and the lessons learned rather than just metrics and numbers. Do your best to create a comprehensive 
        narrative of the week's work. The summary should be a single string of multiple paragraphs. 
        """
    
    @staticmethod
    def create_feedback_prompt(week_state: WeekState)->str:
        return f"""
        You are a helpful assistant optimizing the productivity of an employee who has a certain set of tasks for the week. The employee is
        {week_state.user.username} (ID: {week_state.user.id}). {user.__doc__}
        The employee is part of a team, {week_state.team.team_name} (ID: {week_state.team.id}). {team.__doc__}
        The employee has a certain set of tasks for the week:
        {week_state.tasks}  # {task.__doc__}
        Each task contains:
        {get_class_attributes_docstrings(task)}
        The week you're analyzing is from {week_state.week.start_date} to {week_state.week.end_date}. {week.__doc__}
        This week includes:
        {get_class_attributes_docstrings(week)}

        The employee has asked you to create a feedback on their performance. The feedback should be holistic, and focus less on
        metrics and numbers and more on tips on collaboration, time management, focus, morale and productivity. 
        In addition, if there is enough context on technical challenges faced, please include suggestions on tools, resources,
        techniques or additional training that the employee could use to improve their performance.
        This could mean suggesting a new software library, or a different sales technique, or a new management strategy.
        """
