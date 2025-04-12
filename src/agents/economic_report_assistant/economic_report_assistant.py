from datetime import datetime
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode

from agents.economic_report_assistant.tools import TaoToTrinhKinhPhiTool
from core import get_model, settings


class AgentState(MessagesState, total=False):
    """`total=False` is PEP589 specs.

    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    data: dict
    remaining_steps: RemainingSteps


tools = [TaoToTrinhKinhPhiTool()]
current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
Bạn là một trợ lí ảo giỏi với khả năng tạo tờ trình xin kinh phí.

Ngày hôm nay là {current_date}.

LƯU Ý: NGƯỜI DÙNG KHÔNG THỂ NHÌN THẤY PHẢN HỒI CỦA CÔNG CỤ.

Một số lưu ý khác:
- Trả lời bằng tiếng việt
- Không đưa ra đường dẫn docx
"""


def wrap_model(model: BaseChatModel) -> RunnableSerializable[AgentState, AIMessage]:
    model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | model


async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    if state["remaining_steps"] < 2 and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, need more steps to process this request.",
                )
            ]
        }

    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


def pending_tool_calls(state: AgentState) -> Literal["tools", "done"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(last_message)}")
    if last_message.tool_calls:
        return "tools"
    return "done"


# Define the graph
agent = StateGraph(AgentState)

# Define nodes
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.set_entry_point("model")

# Always run "model" after "tools"
agent.add_edge("tools", "model")

# After "model", if there are tool calls, run "tools". Otherwise END.
agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})

economic_report_assistant = agent.compile(checkpointer=MemorySaver())
