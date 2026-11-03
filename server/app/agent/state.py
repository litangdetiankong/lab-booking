from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class BookingInfo(TypedDict, total=False):
    date: str
    start_time: str
    end_time: str
    people: int
    lab_preference: str

class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]   # 对话历史（add_messages 负责追加而非覆盖）
    booking: BookingInfo                      # 已提取的预约要素
    proposal: str                             # 给用户看的推荐方案
    awaiting_confirm: bool                    # 是否在等用户确认（Human-in-the-loop 开关）
    user_id: int                              # 当前登录用户，落库时用
    candidates: list                          # 本轮候选实验室 [{id, name, capacity, location}]
    intent: str                               # book | qa
