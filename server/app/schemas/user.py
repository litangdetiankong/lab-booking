from pydantic import BaseModel, Field, ConfigDict
class ProfileUpdate(BaseModel):
    nickname: str | None = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=32)   # 新密码同样过入口海关

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # 允许从 ORM 对象读取
    id: int
    username: str
    nickname: str
    avatar: str
    role: str

class AdminUserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    nickname: str = Field(min_length=1, max_length=50)
    role: str = "employee"

class AdminUserUpdate(BaseModel):
    nickname: str = Field(min_length=1, max_length=50)
    role: str