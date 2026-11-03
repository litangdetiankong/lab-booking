import json
import logging
import re
from datetime import date

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState
from app.core.exceptions import BusinessError
from app.core.llm import llm
from app.db.database import SessionLocal
from app.services import lab_service, reservation_service

logger = logging.getLogger("app.agent")

REQUIRED_FIELDS = ("date", "start_time", "end_time", "people")
FIELD_NAMES = {"date": "日期", "start_time": "开始时间", "end_time": "结束时间", "people": "人数"}

CLASSIFY_PROMPT = """判断用户最新一句话的目的，只输出一个词：
book（想预约检测室，或正在补充日期、时间、人数、检测室偏好）
qa（问制度、生物安全、仪器、检测室信息，或其他与新建预约无关的问题）"""

INTENT_PROMPT = """判断用户最新回复的意图，只输出一个词：
confirm（确认下单）/ modify（要改需求）/ cancel（不约了）。
用户的说法可能很随意，比如"行""就要第一个""ok""算了"。"""

_ORDINALS = {
    1: ("第一个", "第1个", "第一间", "第1间"),
    2: ("第二个", "第2个", "第二间", "第2间"),
    3: ("第三个", "第3个", "第三间", "第3间"),
    4: ("第四个", "第4个", "第四间", "第4间"),
    5: ("第五个", "第5个", "第五间", "第5间"),
}


def _message_text(message) -> str:
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = getattr(message, "content", "")
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(str(part.get("text", "")))
            else:
                parts.append(str(part))
        return "".join(parts)
    return str(content or "")


def _last_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    if not messages:
        return ""
    return _message_text(messages[-1])


def _parse_json_obj(text: str) -> dict:
    raw = (text or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        matched = re.search(r"\{.*\}", raw, flags=re.S)
        if not matched:
            return {}
        try:
            data = json.loads(matched.group(0))
        except json.JSONDecodeError:
            return {}
    return data if isinstance(data, dict) else {}


def _booking_active(state: AgentState) -> bool:
    if state.get("awaiting_confirm"):
        return True
    booking = state.get("booking") or {}
    return any(booking.get(key) for key in (*REQUIRED_FIELDS, "lab_preference"))


def _missing(state: AgentState) -> list[str]:
    booking = state.get("booking") or {}
    return [key for key in REQUIRED_FIELDS if not booking.get(key)]


def _catalog(candidates: list[dict]) -> str:
    lines = []
    for index, item in enumerate(candidates, start=1):
        lines.append(f"{index}. {item['name']}｜容纳{item['capacity']}人｜{item['location']}")
    return "\n".join(lines)


def _quick_intent(text: str) -> str | None:
    raw = text.strip()
    if any(word in raw for word in ("不约", "算了", "取消", "不用了", "不要了")):
        return "cancel"
    if any(word in raw for word in ("改成", "换成", "修改", "改到", "换个", "重新")):
        return "modify"
    if raw.lower() in {"行", "ok", "嗯", "好", "yes", "要", "确认", "确定", "可以", "好的", "同意"}:
        return "confirm"
    if any(word in raw for word in ("确认", "确定", "可以", "好的", "就要", "同意", "选")):
        return "confirm"
    if any(word in raw for word in ("第一个", "第二个", "第三个", "第1", "第2", "第3")):
        return "confirm"
    if re.search(r"\d+\s*号", raw):
        return "confirm"
    return None


def pick_lab(candidates: list[dict], user_text: str, proposal: str) -> int | None:
    """只从本轮候选里选实验室。序号按列表顺序，不使用被模型改写过的编号。"""
    if not candidates:
        return None
    text = user_text.strip()
    for index, words in _ORDINALS.items():
        if index <= len(candidates) and any(word in text for word in words):
            return candidates[index - 1]["id"]

    for pattern in (r"(?:编号|选|要)\s*(\d+)", r"(\d+)\s*号", r"^(\d+)$"):
        matched = re.search(pattern, text)
        if not matched:
            continue
        number = int(matched.group(1))
        if 1 <= number <= len(candidates):
            return candidates[number - 1]["id"]
        return None

    for item in candidates:
        name = item.get("name") or ""
        if name and name in text:
            return item["id"]

    if re.search(r"\d|第", text):
        return None
    if proposal:
        mentioned = []
        for item in candidates:
            name = item.get("name") or ""
            position = proposal.find(name) if name else -1
            if position >= 0:
                mentioned.append((position, item["id"]))
        if mentioned:
            mentioned.sort()
            return mentioned[0][1]
    return candidates[0]["id"]


def _cleared_booking() -> dict:
    return {"awaiting_confirm": False, "booking": {}, "candidates": [], "proposal": ""}


def classify(state: AgentState) -> dict:
    if _booking_active(state):
        return {"intent": "book"}
    response = llm.invoke([
        {"role": "system", "content": CLASSIFY_PROMPT},
        {"role": "user", "content": _last_text(state)},
    ])
    word = _message_text(response).strip().lower()
    return {"intent": "book" if "book" in word else "qa"}


def route_intent(state: AgentState) -> str:
    if state.get("intent") == "qa":
        return "answer_qa"
    if state.get("awaiting_confirm"):
        intent = judge_intent(state)
        if intent == "confirm":
            return "create_reservation"
        if intent == "cancel":
            return "cancel_booking"
        return "revise"
    return "extract_info"


def answer_qa(state: AgentState) -> dict:
    from app.services.ai_service import chat as qa_chat

    try:
        reply = qa_chat(_messages_as_dicts(state.get("messages") or []))
    except Exception:
        logger.exception("制度问答失败")
        reply = "暂时没能查到资料，请稍后再试。"
    if not isinstance(reply, str):
        reply = _message_text(reply)
    return {"messages": [AIMessage(content=reply or "暂时没有可回答的内容。")]}


def _messages_as_dicts(messages) -> list[dict]:
    rows = []
    for message in messages:
        if isinstance(message, dict):
            role = message.get("role") or "user"
        else:
            kind = getattr(message, "type", "")
            role = {"human": "user", "ai": "assistant", "system": "system"}.get(kind, "user")
        rows.append({"role": role, "content": _message_text(message)})
    return rows


def extract_info(state: AgentState) -> dict:
    today = date.today().isoformat()
    prompt = f"""你是预约信息提取器。从对话中提取预约要素，只输出 JSON，不要输出任何其他文字：
{{"date": "YYYY-MM-DD", "start_time": "HH:MM", "end_time": "HH:MM", "people": 数字, "lab_preference": "偏好或空字符串"}}
今天的日期是 {today}。"明天下午"这类相对说法要换算成具体日期和时段（下午按 14:00-18:00）。
没提到的键直接省略，不要编造。"""
    response = llm.invoke([
        {"role": "system", "content": prompt},
        *state.get("messages", [])[-6:],
    ])
    info = _parse_json_obj(_message_text(response))
    booking = {**state.get("booking", {}), **{key: value for key, value in info.items() if value}}
    if "people" in booking:
        try:
            booking["people"] = int(booking["people"])
        except (TypeError, ValueError):
            booking.pop("people", None)
    return {"booking": booking}


def after_extract(state: AgentState) -> str:
    return "search_labs" if not _missing(state) else "ask_clarify"


def ask_clarify(state: AgentState) -> dict:
    missing = _missing(state)
    hint = "、".join(FIELD_NAMES[key] for key in missing)
    response = llm.invoke([
        {"role": "system", "content": "你是医药检测实验室预约助手。用一句话自然地向用户追问缺少的信息，不要罗列技术字段名。"},
        {"role": "user", "content": f"用户想预约检测室，还缺少：{hint}。请生成追问。"},
    ])
    return {"messages": [response]}


def revise(state: AgentState) -> dict:
    """用户要改需求：先放下确认闸门，再让提取节点读取这句修改。"""
    return {"awaiting_confirm": False}


def search_labs_node(state: AgentState) -> dict:
    booking = state.get("booking") or {}
    db = SessionLocal()
    try:
        try:
            people = int(booking["people"])
        except (KeyError, TypeError, ValueError):
            return {
                "candidates": [],
                "messages": [AIMessage(content="还需要知道大概人数，才能筛选坐得下的检测室。")],
            }
        labs = lab_service.list_labs(
            db,
            keyword=booking.get("lab_preference") or "",
            capacity_min=people,
            status="开放中",
        )
        candidates = [
            {"id": lab.id, "name": lab.name, "capacity": lab.capacity, "location": lab.location}
            for lab in labs
        ]
        if not candidates:
            return {
                "candidates": [],
                "proposal": "",
                "messages": [AIMessage(content="没有找到符合条件的开放检测室，可以换个时间、人数或偏好再试。")],
            }
        return {"candidates": candidates}
    finally:
        db.close()


def after_search(state: AgentState) -> str:
    return "propose" if state.get("candidates") else "end"


def propose(state: AgentState) -> dict:
    booking = state.get("booking") or {}
    catalog = _catalog(state.get("candidates") or [])
    response = llm.invoke([
        {"role": "system", "content":
            "你是医药检测预约助手。根据候选检测室和用户需求给出推荐。"
            "候选前面的序号就是用户要回复的序号，请沿用这些序号和名称，不要另编编号。"
            "最后请用户回复序号确认。"},
        {"role": "user", "content":
            f"需求：{booking.get('date')} {booking.get('start_time')}-{booking.get('end_time')}，"
            f"{booking.get('people')} 人。\n候选：\n{catalog}"},
    ])
    return {"messages": [response], "proposal": _message_text(response), "awaiting_confirm": True}


def judge_intent(state: AgentState) -> str:
    quick = _quick_intent(_last_text(state))
    if quick:
        return quick
    response = llm.invoke([
        {"role": "system", "content": INTENT_PROMPT},
        {"role": "user", "content": _last_text(state)},
    ])
    word = _message_text(response).strip().lower()
    if word in ("confirm", "modify", "cancel"):
        return word
    return "modify"


def cancel_booking(state: AgentState) -> dict:
    return {
        "messages": [AIMessage(content="好的，这次预约已取消。需要的话可以重新告诉我时间、人数和偏好。")],
        **_cleared_booking(),
    }


def create_reservation(state: AgentState) -> dict:
    candidates = state.get("candidates") or []
    lab_id = pick_lab(candidates, _last_text(state), state.get("proposal") or "")
    if lab_id is None:
        return {
            "messages": [AIMessage(content="没能确定要预约哪一间。请直接回复序号，例如 1 或 2。")],
            "awaiting_confirm": True,
        }
    user_id = state.get("user_id")
    if not user_id:
        return {
            "messages": [AIMessage(content="预约失败：未识别到登录用户，请重新登录后再试。")],
            "awaiting_confirm": True,
        }
    booking = state.get("booking") or {}
    db = SessionLocal()
    try:
        reservation = reservation_service.create(
            db,
            user_id=user_id,
            lab_id=lab_id,
            d=booking["date"],
            start=booking["start_time"],
            end=booking["end_time"],
            purpose="检验助手代预约",
        )
        return {
            "messages": [AIMessage(content=f"预约成功！单号 {reservation.id}，状态：待审核。")],
            **_cleared_booking(),
        }
    except BusinessError as exc:
        return {
            "messages": [AIMessage(content=f"预约失败：{exc.message}")],
            "awaiting_confirm": True,
        }
    except Exception:
        logger.exception("AI 预约落库失败")
        return {
            "messages": [AIMessage(content="预约失败，请稍后再试。")],
            "awaiting_confirm": True,
        }
    finally:
        db.close()


builder = StateGraph(AgentState)
builder.add_node("classify", classify)
builder.add_node("answer_qa", answer_qa)
builder.add_node("extract_info", extract_info)
builder.add_node("ask_clarify", ask_clarify)
builder.add_node("search_labs", search_labs_node)
builder.add_node("propose", propose)
builder.add_node("revise", revise)
builder.add_node("cancel_booking", cancel_booking)
builder.add_node("create_reservation", create_reservation)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_intent, {
    "answer_qa": "answer_qa",
    "extract_info": "extract_info",
    "create_reservation": "create_reservation",
    "cancel_booking": "cancel_booking",
    "revise": "revise",
})
builder.add_edge("answer_qa", END)
builder.add_edge("revise", "extract_info")
builder.add_conditional_edges("extract_info", after_extract, {
    "ask_clarify": "ask_clarify",
    "search_labs": "search_labs",
})
builder.add_edge("ask_clarify", END)
builder.add_conditional_edges("search_labs", after_search, {
    "propose": "propose",
    "end": END,
})
builder.add_edge("propose", END)
builder.add_edge("cancel_booking", END)
builder.add_edge("create_reservation", END)

checkpointer = MemorySaver()
agent = builder.compile(checkpointer=checkpointer)
