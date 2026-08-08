from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator


# --- USER SCHEMAS ---
class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- PROJECT SCHEMAS ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = ""
    owner_id: int


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- TASK SCHEMAS ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Literal["low", "medium", "high"] = "medium"
    
    # date -> str (Plain text due dates support)
    due_date: Optional[str] = None
    
    completed: bool = False
    user_id: int
    project_id: Optional[int] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value):
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("title must be a string")
        value = value.strip()
        if not value:
            raise ValueError("title cannot be empty")
        return value


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    
    # date -> str
    due_date: Optional[str] = None
    
    completed: Optional[bool] = None
    user_id: Optional[int] = None
    project_id: Optional[int] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value):
        if value is None:
            return value
        if not isinstance(value, str):
            raise ValueError("title must be a string")
        value = value.strip()
        if not value:
            raise ValueError("title cannot be empty")
        return value


class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- EXTRA SCHEMAS ---
class QuickAddRequest(BaseModel):
    description: str
    user_id: int
    project_id: Optional[int] = None


class ProjectStatResponse(BaseModel):
    project_id: int
    project_name: str
    task_count: int