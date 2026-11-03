from pydantic import BaseModel

class LabOut(BaseModel):
    """列表项的形状。想加字段就改这里——所有调用方同步感知"""
    id: int
    name: str
    location: str
    capacity: int
    status: str