from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes_file import router as file_router
from api.routes_task import router as task_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
	"http://localhost:3001",
        "https://ultra-frontend-569094769218.asia-east1.run.app"
	],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(file_router)
app.include_router(task_router)

@app.get("/")
def root():
    return {"status": "V5.2 Fully Active"}
