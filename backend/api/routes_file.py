from fastapi import APIRouter
from pydantic import BaseModel
from tools.file_tool import *

router = APIRouter()

class FileData(BaseModel):
    name: str
    content: str

@router.get("/files")
def files():
    return list_files()

@router.get("/file/{name}")
def get_file(name: str):
    return {"content": read_file(name)}

@router.post("/file")
def save(data: FileData):
    return {"status": write_file(data.name, data.content)}
