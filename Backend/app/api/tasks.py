from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai_service import generate_subtasks
from app.core.algorithms import binary_search, insertion_sort, linear_search, parse_quick_add
from app.database import get_db
from app.models.task import Project, Task, User
from app.schemas.task import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatResponse,
    ProjectUpdate,
    QuickAddRequest,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/api", tags=["tasks"])


class AISuggestRequest(BaseModel):
    title: str


def to_response(schema_cls, instance):
    if hasattr(schema_cls, "model_validate"):
        return schema_cls.model_validate(instance)
    return schema_cls.from_orm(instance)


# ==========================================
# USER ROUTES
# ==========================================

@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [to_response(UserResponse, user) for user in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(name=payload.name, email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_response(UserResponse, user)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_response(UserResponse, user)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = payload.name
    user.email = payload.email
    db.commit()
    db.refresh(user)
    return to_response(UserResponse, user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None


# ==========================================
# PROJECT ROUTES
# ==========================================

@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [to_response(ProjectResponse, project) for project in projects]


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    owner = db.query(User).filter(User.id == payload.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    project = Project(name=payload.name, description=payload.description, owner_id=payload.owner_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return to_response(ProjectResponse, project)


# NOTE: /projects/stats MUST come BEFORE /projects/{project_id}
@router.get("/projects/stats", response_model=list[ProjectStatResponse])
def get_project_stats(db: Session = Depends(get_db)):
    stats = (
        db.query(
            Project.id.label("project_id"),
            Project.name.label("project_name"),
            func.count(Task.id).label("task_count"),
        )
        .outerjoin(Task, Task.project_id == Project.id)
        .group_by(Project.id, Project.name)
        .all()
    )
    return [
        ProjectStatResponse(project_id=row.project_id, project_name=row.project_name, task_count=row.task_count)
        for row in stats
    ]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return to_response(ProjectResponse, project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.owner_id is not None:
        owner = db.query(User).filter(User.id == payload.owner_id).first()
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")
        project.owner_id = payload.owner_id
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.commit()
    db.refresh(project)
    return to_response(ProjectResponse, project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return None


# ==========================================
# TASK ROUTES
# ==========================================

@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(sort: Optional[str] = Query(default=None), db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    if sort:
        task_dicts = [{"title": t.title, "priority": t.priority, "id": t.id, "_orm": t} for t in tasks]
        sort_key = sort if sort in ["priority", "title", "id"] else "priority"
        insertion_sort(task_dicts, key=sort_key)
        tasks = [d["_orm"] for d in task_dicts]

    return [to_response(TaskResponse, task) for task in tasks]


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.project_id is not None:
        project = db.query(Project).filter(Project.id == payload.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    task = Task(
        title=payload.title,
        description=payload.description or "",
        priority=payload.priority,
        due_date=payload.due_date,
        completed=payload.completed,
        user_id=payload.user_id,
        project_id=payload.project_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return to_response(TaskResponse, task)


# NOTE: /tasks/search MUST come BEFORE /tasks/{task_id}
@router.get("/tasks/search", response_model=list[TaskResponse])
def search_tasks(title: str = "", algo: str = "binary", db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    if not title:
        return [to_response(TaskResponse, task) for task in tasks]

    task_dicts = [{"title": task.title.lower(), "_orm": task} for task in tasks]
    search_title = title.lower()

    if algo.lower() == "binary":
        insertion_sort(task_dicts, key="title")
        match_index = binary_search(task_dicts, target_value=search_title, key="title")
    else:
        match_index = linear_search(task_dicts, target_value=search_title, key="title")

    # Fix: Raise 404 Exception ki jagah empty list [] return karein (HTTP 200 OK)
    if match_index == -1 or match_index is None:
        return []

    selected_task = task_dicts[match_index]["_orm"]
    return [to_response(TaskResponse, selected_task)]


# NOTE: /tasks/quick-add MUST come BEFORE /tasks/{task_id}
@router.post("/tasks/quick-add", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def quick_add_task(payload: QuickAddRequest, db: Session = Depends(get_db)):
    if payload.project_id is not None:
        project = db.query(Project).filter(Project.id == payload.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Project with provided project_id does not exist"
            )

    user_id = getattr(payload, "user_id", None)
    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="User not found"
            )

    parsed = parse_quick_add(payload.description)
    task = Task(
        title=parsed["title"],
        description=payload.description,
        priority=parsed["priority"],
        due_date=parsed.get("due_date_hint"),
        user_id=user_id,
        project_id=payload.project_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return to_response(TaskResponse, task)


# NOTE: /tasks/ai-suggest MUST come BEFORE /tasks/{task_id}
@router.post("/tasks/ai-suggest")
def ai_suggest_subtasks(payload: AISuggestRequest):
    if not payload.title:
        raise HTTPException(status_code=400, detail="Task title zaroori hai")

    try:
        suggestions = generate_subtasks(payload.title)
        return {
            "success": True,
            "title": payload.title,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return to_response(TaskResponse, task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.user_id is not None:
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        task.user_id = payload.user_id
    if payload.project_id is not None:
        project = db.query(Project).filter(Project.id == payload.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        task.project_id = payload.project_id
    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.priority is not None:
        task.priority = payload.priority
    if payload.due_date is not None:
        task.due_date = payload.due_date
    if payload.completed is not None:
        task.completed = payload.completed
    db.commit()
    db.refresh(task)
    return to_response(TaskResponse, task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None