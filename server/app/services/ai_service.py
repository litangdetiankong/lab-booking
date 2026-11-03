from app.core.llm import llm, SYSTEM_PROMPT
from app.services import rag_service
from app.services.ai_tools import search_labs, get_lab_equipment   # ← 片段没带 import，漏了就是 NameError

tools = [search_labs, get_lab_equipment]
llm_with_tools = llm.bind_tools(tools)
TOOLBOX = {t.name: t for t in tools}          # 白名单：name → 函数（安全边界）

def chat(messages: list[dict]) -> str:
    # 先做 RAG（11 步成果）：检索制度片段拼进 system——与工具循环是叠加关系
    question = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
    hits = rag_service.retrieve(question)
    system = SYSTEM_PROMPT
    if hits:
        context = "\n---\n".join(hits)
        system += (f"\n\n以下是公司检测管理制度的相关片段，回答时优先依据它们并注明依据；"
                   f"片段不足以回答时，明确告知用户你不知道：\n{context}")

    msgs = [{"role": "system", "content": system}] + messages
    for _ in range(8):                        # 循环上限：防止模型反复要工具形成死循环
        resp = llm_with_tools.invoke(msgs)
        if not resp.tool_calls:               # 模型不再要工具 → 这就是最终回答
            return resp.content
        msgs.append(resp)                     # 把"我要用工具"的决定也记进上下文
        for call in resp.tool_calls:
            fn = TOOLBOX.get(call["name"])    # 白名单校验：模型输出是不可信输入！
            if fn is None:
                result = f"未知工具：{call['name']}"
            else:
                result = str(fn.invoke(call["args"]))   # 真正执行的地方，全项目仅此一处
            msgs.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    return "抱歉，这个请求太复杂了，请换个说法或分步描述。"