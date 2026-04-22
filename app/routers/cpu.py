from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config
from utils.prometheus import cpu_total_usage, get_prometheus_metrics

router = APIRouter()

@router.get("/metrics/cpu", tags=["cpu"])
async def get_cpu_metrics():
    """
    Queries Prometheus for the current CPU usage system metric.
    """
    return await handle_api_response(
        get_prometheus_metrics,
        get_config("PROMETHEUS_URL"),
        "cpu_usage_system"
    )

@router.get("/usage/cpu", tags=["cpu"])
async def get_cpu_total_usage():
    """
    Queries Prometheus for the current CPU usage system metric.
    """
    return await handle_api_response(
        cpu_total_usage,
        get_config("PROMETHEUS_URL")
    )
