from langgraph.graph import StateGraph, START, END

from app.core.agentic.agent_workflows.base_agent_workflow import BaseAgentWorkflow
from app.core.agentic.agent_functions.week_analysis_functions import (
    WeekAnalysisFunctions,
)


class CreateWeekWorkflow(BaseAgentWorkflow):
    """Workflow for generating appeal content using AppealV2State."""

    @staticmethod
    def build_edges(graph: StateGraph):
        """Build the edges for the appeal generated workflow."""
        cwf = WeekAnalysisFunctions

        # Define workflow edges
        graph.add_edge(START, cwf.create_summary_key())
        graph.add_edge(cwf.create_summary_key(), cwf.create_feedback_key())
        graph.add_edge(cwf.create_feedback_key(), END)

        return graph
