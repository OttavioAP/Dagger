from abc import abstractmethod

from langgraph.graph import StateGraph
from pydantic import BaseModel

from app.core.agentic.agent_workflows.base_agent_workflow import BaseAgentWorkflow
from app.core.agentic.agent_functions.base_agent_function import BaseAgentFunction
from pydantic import BaseModel
from app.core.logger import logger


def build_agent_mappings():
    """
    Builds a dictionary of agent functions using all of the mappings in the subclasses of AgentFunction.
    """
    agent_map: dict = {}

    agent_functions = BaseAgentFunction.__subclasses__()

    for agent_function in agent_functions:
        agent_map.update(agent_function().add_mappings())

    logger.info(f"Agent map: {agent_map}")
    return agent_map


class AgentService:
    @staticmethod
    def graph(workflow: BaseAgentWorkflow, state_class: type[BaseModel]):
        """
        Builds the graph for the agent.
        """
        graph = StateGraph(state_class)
        for agent_function_key, agent_function in build_agent_mappings().items():
            logger.debug(f"Adding node: {agent_function_key}")
            graph.add_node(agent_function_key, agent_function)

        graph = workflow.build_edges(graph)
        return graph.compile()

    @staticmethod
    async def invoke(workflow: BaseAgentWorkflow, state: BaseModel):
        """
        Invokes the agent.
        """
        return await AgentService.graph(workflow, state.__class__).ainvoke(state)
