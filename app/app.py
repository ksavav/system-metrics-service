from fastapi import FastAPI, HTTPException

from utils.config import get_config
from utils.prometheus import get_cpu_total_metric

app = FastAPI()

PROMETHEUS_URL = get_config("PROMETHEUS_URL")

@app.get("/api/metrics/cpu")
async def get_cpu_metrics():
    """
    Queries Prometheus for the current CPU usage system metric.
    """
    try:
        cpu_metrics = await get_cpu_total_metric(PROMETHEUS_URL)
        return {"status": "success", "data": cpu_metrics}
    except HTTPException as e:
        return {"status": "error", "detail": str(e.detail)}
