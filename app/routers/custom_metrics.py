import asyncio
from collections import defaultdict

from fastapi import APIRouter, FastAPI, Response
from prometheus_client import Gauge, generate_latest

from utils.config import get_config
from utils.drm_gpu import map_render_to_card, monitor_gpu_metrics
from utils.logger import log

router = APIRouter()


GAUGES = defaultdict(str)
async def gather_drm_metric():
    gpus_list = map_render_to_card()
    interval = int(get_config("INTERVAL", 5))

    while True:
        try:
            calculated_gpu_metrics = monitor_gpu_metrics(gpus_list, interval)
            print(calculated_gpu_metrics)
            for render in calculated_gpu_metrics:
                for k, v in calculated_gpu_metrics[render].items():
                    if k not in GAUGES:
                        GAUGES[k] = Gauge(
                            name=k,
                            documentation="",
                            labelnames=["status", "device"]
                        )
                        GAUGES[k].labels(status='success', device=render).set(v)
                    else:
                        GAUGES[k].labels(status='success', device=render).set(v)
        except Exception as e:
            log.error(f"Error during getting DRM data: {e}")
            for g in GAUGES:
                GAUGES[g].labels(status='error', device=None).set(0)

        await asyncio.sleep(interval)

async def lifespan(app: FastAPI):
    task = asyncio.create_task(gather_drm_metric())
    yield
    task.cancel()

@router.get("/metrics")
def get_metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

