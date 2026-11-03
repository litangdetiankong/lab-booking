from fastapi.responses import JSONResponse

def ok(data=None, message="ok"):
    """成功响应：业务代码直接 return 这个 dict，FastAPI 自动序列化成 JSON"""
    return {"code": 0, "message": message, "data": data}

def fail(code: int, message: str, http_status: int = 400):
    """失败响应：需要控制 HTTP 状态码时用它（返回 JSONResponse 而不是 dict）
    大多数业务失败走 BusinessError 全局处理器，这个助手用于个别特殊场景"""
    return JSONResponse(
        status_code=http_status,      # HTTP 层状态码：网关/监控靠它识别异常流量
        content={"code": code, "message": message, "data": None},
    )