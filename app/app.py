from fastapi import FastAPI

from routers import cpu, gpu

app = FastAPI()

app.include_router(cpu.router, prefix="/api")
app.include_router(gpu.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello there!"}
