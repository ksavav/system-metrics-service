from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config
from utils.prometheus import get_and_extract_metric

router = APIRouter()

@router.get("/metrics/memory/total", tags=["memory"])
async def get_memory_total_metrics():
    return await handle_api_response(
        get_and_extract_metric,
        get_config("PROMETHEUS_URL"),
        "mem_total",
        "__name__",
        "mem_total"
    )

@router.get("/metrics/memory/free", tags=["memory"])
async def get_memory_free_metrics():
    return await handle_api_response(
        get_and_extract_metric,
        get_config("PROMETHEUS_URL"),
        "mem_free",
        "__name__",
        "mem_free"
    )

@router.get("/metrics/memory/used", tags=["memory"])
async def get_memory_used_metrics():
    return await handle_api_response(
        get_and_extract_metric,
        get_config("PROMETHEUS_URL"),
        "mem_used",
        "__name__",
        "mem_used"
    )

@router.get("/usage/memory", tags=["memory"])
async def get_memory_usage():
    return await handle_api_response(
        get_and_extract_metric,
        get_config("PROMETHEUS_URL"),
        "mem_used_percent",
        "__name__",
        "mem_used_percent"
    )
