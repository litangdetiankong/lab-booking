import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.graph import agent, checkpointer
from app.api.deps import get_current_user
from app.core.exceptions import BusinessError
from app.core.response import ok
from app.db.models import User

logger = logging.getLogger("app.ai")
router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]        # 前端仍带完整历史（用于展示）；agent 只取最新一句


def _latest(data: ChatRequest) -> str:
    if not data.messages:
        raise BusinessError(3201, "请输入内容")
    text = str(data.messages[-1].get("content") or "").strip()
    if not text:
        raise BusinessError(3201, "请输入内容")
    return text


def _thread(user: User) -> dict:
    return {"configurable": {"thread_id": f"u{user.id}"}}


def _turn(user: User, text: str) -> dict:
    return {
        "messages": [{"role": "user", "content": text}],
        "user_id": user.id,
    }


@router.post("/chat")
def chat(data: ChatRequest, user: User = Depends(get_current_user)):
    result = agent.invoke(_turn(user, _latest(data)), config=_thread(user))
    return ok({"reply": result["messages"][-1].content})


@router.post("/chat/reset")
def reset_chat(user: User = Depends(get_current_user)):
    """清空该用户的预约对话记忆。前端「清空对话」必须调用，否则下一句还会接着上一轮预约。"""
    checkpointer.delete_thread(f"u{user.id}")
    return ok(None)


def event(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
def chat_stream(data: ChatRequest, user: User = Depends(get_current_user)):
    def gen():
        yield event({"type": "start"})
        try:
            text = _latest(data)
        except BusinessError as exc:
            yield event({"type": "error", "message": exc.message})
            yield event({"type": "done"})
            return
        try:
            for chunk in agent.stream(_turn(user, text), config=_thread(user), stream_mode="updates"):
                for node_name, update in chunk.items():
                    yield event({"type": "node", "name": node_name})
                    content = ""
                    if update and update.get("messages"):
                        content = str(update["messages"][-1].content)
                    elif update and update.get("proposal"):
                        content = update["proposal"]
                    for index in range(0, len(content), 3):
                        yield event({"type": "token", "content": content[index:index + 3]})
        except Exception:
            logger.exception("AI 流式对话失败")
            yield event({"type": "error", "message": "处理失败，请重试"})
        yield event({"type": "done"})

    return StreamingResponse(gen(), media_type="text/event-stream")
