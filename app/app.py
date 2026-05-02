from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import cpu, custom_metrics, disk, gpu, memory, npu
from routers.custom_metrics import lifespan

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# metrics_app = make_asgi_app()
# app.mount("/metrics", metrics_app)

app.include_router(custom_metrics.router)

app.include_router(cpu.router, prefix="/api")
app.include_router(gpu.router, prefix="/api")
app.include_router(npu.router, prefix="/api")
app.include_router(disk.router, prefix="/api")
app.include_router(memory.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello there!"}
