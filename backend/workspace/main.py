from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import math_lib
import database

app = FastAPI(title="Math API", version="1.0")

# Initialize database
database.init_db()

class CalculateRequest(BaseModel):
    operation: str
    operand_a: float
    operand_b: float

class CalculateData(BaseModel):
    id: int
    result: float

class CalculateResponse(BaseModel):
    status: str
    data: CalculateData

class HistoryResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]

@app.get("/")
def serve_index():
    return FileResponse("index.html")

@app.post("/api/v1/calculate", response_model=CalculateResponse)
def calculate(req: CalculateRequest):
    try:
        if req.operation == "add":
            result = math_lib.add(req.operand_a, req.operand_b)
        elif req.operation == "subtract":
            result = math_lib.subtract(req.operand_a, req.operand_b)
        elif req.operation == "multiply":
            result = math_lib.multiply(req.operand_a, req.operand_b)
        elif req.operation == "divide":
            result = math_lib.divide(req.operand_a, req.operand_b)
        else:
            raise ValueError(f"Invalid operation: {req.operation}")
            
        record_id = database.insert_calculation(req.operation, req.operand_a, req.operand_b, result)
        
        return CalculateResponse(
            status="success",
            data=CalculateData(id=record_id, result=result)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/history", response_model=HistoryResponse)
def get_history():
    try:
        history = database.get_history()
        return HistoryResponse(
            status="success",
            data=history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
