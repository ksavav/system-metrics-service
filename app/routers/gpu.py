from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config
from utils.prometheus import (
    get_prometheus_metrics,
    gpu_memory_metrcis,
    gpu_memory_usage,
    gpu_total_usage,
)

router = APIRouter()

@router.get("/metrics/gpu/utilization", tags=["gpu"])
async def get_gpu_utilization_metrics():
    """
    Queries Prometheus for the current GPU usage system metric.
    """
    return await handle_api_response(
        get_prometheus_metrics,
        get_config("PROMETHEUS_URL"),
        "nvidia_smi_utilization_gpu"
    )

@router.get("/metrics/gpu/temperature", tags=["gpu"])
async def get_gpu_temperature_metrics():
    """
    Queries Prometheus for the current GPU temperature system metric.
    """
    return await handle_api_response(
        get_prometheus_metrics,
        get_config("PROMETHEUS_URL"),
        "nvidia_smi_temperature_gpu"
    )

@router.get("/metrics/gpu/memory", tags=["gpu"])
async def get_gpu_memory_metrics():
    """
    Queries Prometheus for the current GPU memory system metric.
    """
    return await handle_api_response(
        gpu_memory_metrcis,
        get_config("PROMETHEUS_URL")
    )

@router.get("/usage/gpu", tags=["gpu"])
async def get_gpu_total_usage():
    """
    Queries Prometheus for the current GPU usage system metric.
    """
    return await handle_api_response(
        gpu_total_usage,
        get_config("PROMETHEUS_URL")
    )

@router.get("/usage/gpu/memory", tags=["gpu"])
async def get_gpu_memory_usage():
    """
    Queries Prometheus for the current GPU memory system metric.
    """
    return await handle_api_response(
        gpu_memory_usage,
        get_config("PROMETHEUS_URL")
    )
