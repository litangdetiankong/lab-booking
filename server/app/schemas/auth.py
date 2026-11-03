from pydantic import BaseModel
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)   # 入口海关：长度不合法直接 422，到不了 service
    password: str = Field(min_length=6, max_length=32)   # 明文密码只存在于请求到达的一瞬间
    nickname: str = Field(min_length=1, max_length=50)
