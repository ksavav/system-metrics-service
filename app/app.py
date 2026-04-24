from fastapi import FastAPI

from routers import cpu, disk, gpu, memory, npu

app = FastAPI()

app.include_router(cpu.router, prefix="/api")
app.include_router(gpu.router, prefix="/api")
app.include_router(npu.router, prefix="/api")
app.include_router(memory.router, prefix="/api")
app.include_router(disk.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello there!"}
