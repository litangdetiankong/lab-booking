import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, labs, reservations, ai, stats
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import BusinessError
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="医药检测实验室预约系统")
app.add_middleware(                              
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api/users") 
app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.include_router(labs.router, prefix="/api/labs")
app.include_router(reservations.router, prefix="/api/reservations")
app.include_router(ai.router, prefix="/api/ai") 
app.include_router(stats.router, prefix="/api/stats")

@app.get("/api/ping")
def ping():
    return {"code": 0, "message": "ok", "data": "pong"}

@app.exception_handler(BusinessError)
async def on_business(request: Request, exc: BusinessError):
    return JSONResponse(status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None})

@app.exception_handler(RequestValidationError)
async def on_validate(request: Request, exc: RequestValidationError):
    """参数校验失败（Pydantic 抛的 422）：把啰嗦的错误收敛成一句话给前端"""
    first = exc.errors()[0]                          # 只取第一个错误，别刷屏
    loc = ".".join(str(x) for x in first["loc"][1:]) # loc[0] 是 body/query 这种位置标记，去掉更清爽
    return JSONResponse(status_code=200, content={
        "code": 422,
        "message": f"参数错误：{loc} {first['msg']}",  # 例：参数错误：password String should have at least 6 characters
        "data": None})

@app.exception_handler(Exception)
async def on_unknown(request: Request, exc: Exception):
    """兜底：任何没被预料的异常都到这里——绝不让堆栈泄漏给前端（攻击者拿它分析漏洞）"""
    import logging, traceback
    logging.error("未处理异常 %s %s\n%s",               # 完整堆栈只进服务器日志
                  request.method, request.url.path, traceback.format_exc())
    return JSONResponse(status_code=500, content={
        "code": 500, "message": "服务器开小差了，请稍后再试", "data": None})