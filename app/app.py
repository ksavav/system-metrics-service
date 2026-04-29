import asyncio

from fastapi import FastAPI
from prometheus_client import Gauge, make_asgi_app

from routers import cpu, disk, gpu, memory, npu
from utils.config import get_config
from utils.drm_gpu import map_render_to_card, monitor_gpu_metrics
from utils.logger import log

DRM_METRICS = Gauge(
    'metric_name',
    'description',
    ['status']
)

async def gather_drm_metric():
    gpus_list = map_render_to_card()
    interval = int(get_config("INTERVAL", 5))

    while True:
        try:
            drm_values, calculated_gpu_metrics = monitor_gpu_metrics(gpus_list, interval)
            DRM_METRICS.labels(status='success').set(drm_values)

        except Exception:
            log.error("Error during getting DRM data", exc_info=True)
            DRM_METRICS.labels(status='error').set(0)

        await asyncio.sleep(interval)

async def lifespan(app: FastAPI):
    task = asyncio.create_task(gather_drm_metric())

    yield

    task.cancel()


app = FastAPI(lifespan=lifespan)


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(cpu.router, prefix="/api")
app.include_router(gpu.router, prefix="/api")
app.include_router(npu.router, prefix="/api")
app.include_router(disk.router, prefix="/api")
app.include_router(memory.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hello there!"}
