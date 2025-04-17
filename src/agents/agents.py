from dataclasses import dataclass

from langgraph.graph.state import CompiledStateGraph

from agents.chatbot import chatbot
from agents.research_assistant.research_assistant import research_assistant
from agents.economic_report_assistant.economic_report_assistant import economic_report_assistant
from schema import AgentInfo

DEFAULT_AGENT = "research-assistant"


@dataclass
class Agent:
    description: str
    graph: CompiledStateGraph


agents: dict[str, Agent] = {
    "chatbot": Agent(description="A simple chatbot.", graph=chatbot),
    "research-assistant": Agent(
        description="A research assistant with web search and calculator.", graph=research_assistant
    ),
    "economic-report-assistant": Agent(description="A economic report assistant.", graph=economic_report_assistant),
}


def get_agent(agent_id: str) -> CompiledStateGraph:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()]
