from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config
from utils.prometheus import get_and_extract_all_metrics, get_and_extract_metric

router = APIRouter()

@router.get("/metrics/cpu", tags=["cpu"])
async def get_cpu_metrics():
    """
    Queries Prometheus for the current CPU usage system metric.
    """
    return await handle_api_response(
        get_and_extract_all_metrics,
        get_config("PROMETHEUS_URL"),
        "cpu_usage_system",
        "cpu"
    )

@router.get("/usage/cpu", tags=["cpu"])
async def get_cpu_total_usage():
    """
    Queries Prometheus for the current CPU usage system metric.
    """
    return await handle_api_response(
        get_and_extract_metric,
        get_config("PROMETHEUS_URL"),
        "cpu_usage_system",
        "__name__",
        "cpu_usage_system"
    )
