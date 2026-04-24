from statistics import mean

from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config
from utils.prometheus import get_and_extract_all_metrics, get_prometheus_metrics

router = APIRouter()

@router.get("/metrics/gpu/utilization", tags=["gpu"])
async def get_gpu_utilization_metrics():
    return await handle_api_response(
        get_and_extract_all_metrics,
        get_config("PROMETHEUS_URL"),
        "nvidia_smi_utilization_gpu",
        "pstate"
    )

@router.get("/metrics/gpu/temperature", tags=["gpu"])
async def get_gpu_temperature_metrics():
    return await handle_api_response(
        get_and_extract_all_metrics,
        get_config("PROMETHEUS_URL"),
        "nvidia_smi_temperature_gpu",
        "pstate"
    )

@router.get("/metrics/gpu/memory", tags=["gpu"])
async def get_gpu_memory_metrics():
    return await handle_api_response(
        gpu_memory_metrcis,
        get_config("PROMETHEUS_URL")
    )

@router.get("/usage/gpu", tags=["gpu"])
async def get_gpu_total_usage():
    return await handle_api_response(
        gpu_total_usage,
        get_config("PROMETHEUS_URL")
    )

@router.get("/usage/gpu/memory", tags=["gpu"])
async def get_gpu_memory_usage():
    return await handle_api_response(
        gpu_memory_usage,
        get_config("PROMETHEUS_URL")
    )

async def gpu_memory_metrcis(prometheus_url: str) -> dict:
    return {
        "free": await get_and_extract_all_metrics(
            prometheus_url,
            "nvidia_smi_memory_free",
            "pstate"
        ),
        "used": await get_and_extract_all_metrics(
            prometheus_url,
            "nvidia_smi_memory_used",
            "pstate"
        ),
        "total": await get_and_extract_all_metrics(
            prometheus_url,
            "nvidia_smi_memory_total",
            "pstate"
        )
    }

async def gpu_total_usage(prometheus_url: str) -> str:
    promql_query = 'nvidia_smi_utilization_gpu'
    response = await get_prometheus_metrics(prometheus_url, promql_query)
    return str(mean(
        float(item.get("value", [None, None])[1])
        for item in response.get("data", {}).get("result", [])
    ))

async def gpu_memory_usage(prometheus_url: str) -> str:
    promql_query = 'nvidia_smi_utilization_memory'
    response = await get_prometheus_metrics(prometheus_url, promql_query)
    return str(mean(
        float(item.get("value", [None, None])[1])
        for item in response.get("data", {}).get("result", [])
    ))
