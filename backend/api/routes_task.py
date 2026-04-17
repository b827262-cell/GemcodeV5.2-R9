from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from core.task_manager import task_manager
from agent_core.loop import engine

router = APIRouter()

class TaskRequest(BaseModel):
    prompt: str
    model: str

@router.post("/task")
async def create_task(req: TaskRequest, bg: BackgroundTasks):
    task_id = task_manager.create(req.prompt, req.model)
    bg.add_task(engine.run, task_id, req.model)
    return {"task_id": task_id}

@router.get("/task/{task_id}")
async def get_task(task_id: str):
    return task_manager.tasks.get(task_id, {"error": "Not found"})
