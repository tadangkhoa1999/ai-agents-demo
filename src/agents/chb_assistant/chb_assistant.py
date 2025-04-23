from datetime import datetime
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode

from agents.chb_assistant.tools import TimKiemKhachHangTool, TaoCoHoiBanTool
from core import get_model, settings


class AgentState(MessagesState, total=False):
    """`total=False` is PEP589 specs.

    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    data: dict
    remaining_steps: RemainingSteps


tools = [TimKiemKhachHangTool(), TaoCoHoiBanTool()]
current_date = datetime.now().strftime("%B %d, %Y")
instructions = f"""
Bạn là một trợ lí ảo giỏi với khả năng nhập cơ hội bán vào hệ thống.

Người dùng có thể tạo cơ hội bán với cú pháp như sau:
Tạo cơ hội bán [Tên khách hàng] - [Số điện thoại] - [Sản phẩm] - [Trạng thái] - [Doanh số đơn vị triệu đồng]

Ví dụ:
Tạo CHB cho KH Nguyễn Thảo Quỳnh Trang - SĐT: 0934351724 - Đã tư vấn - Bond 200 triệu, Banca PNT 24 triệu, FD 100 triệu và KH Chu Phương Quỳnh - SĐT: 0123.358.890 - đã mở tài khoản thành công, Đang tiếp cận Thẻ 100 triệu, đang tư vấn bảo hiểm 20 triệu

Các bước thực hiện:
- Sử dụng công cụ tim_kiem_khach_hang (Tìm kiếm khách hàng) để lấy ID của khách hàng, nếu không tìm thấy hãy dựa vào thông tin lỗi để báo lại người dùng.
- Sử dụng công cụ tao_co_hoi_ban (Tạo cơ hội bán) để tạo cơ hội bán dựa trên: [ID khách hàng], [Sản phẩm], [Trạng thái], [Doanh số đơn vị triệu đồng]. Nếu có lỗi hãy báo lại người dùng.

LƯU Ý: NGƯỜI DÙNG KHÔNG THỂ NHÌN THẤY PHẢN HỒI CỦA CÔNG CỤ.

Một số lưu ý khác:
- Trả lời bằng tiếng việt
- Người dùng không thể nhìn thấy phản hồi của công cụ nên hãy báo các bước thực hiện mà không báo việc sử dụng công cụ.
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

chb_assistant = agent.compile(checkpointer=MemorySaver())
