from fastapi import FastAPI, HTTPException

from routers import cpu, gpu
from utils.config import get_config

app = FastAPI()

PROMETHEUS_URL = get_config("PROMETHEUS_URL")

app.include_router(cpu.router, prefix="/api")
app.include_router(gpu.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello there!"}
