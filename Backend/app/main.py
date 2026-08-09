import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.tasks import router as tasks_router
from app.database import Base, engine
from app.models.task import Project, Task, User

app = FastAPI(title="TaskFlow API")


@app.middleware("http")
async def log_request_duration(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    print(f"{request.method} {request.url.path} completed in {duration:.4f}s")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://blinkit-taskflow.vercel.app",  # <-- Yeh line add karni hai zaroori!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)
app.include_router(tasks_router)


@app.get("/")
def home():
    return {"message": "TaskFlow API is running"}