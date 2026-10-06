from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
# min_length=1 rejects empty titles; FastAPI returns 422 automatically
    title: str = Field(min_length=1)
    description: Optional[str] = None
    completed: bool = False


# All fields optional so PATCH can update just one field at a time
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    completed: Optional[bool] = None

  # Lets Pydantic read values directly from SQLAlchemy objects
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    completed: bool   