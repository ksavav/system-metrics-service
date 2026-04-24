from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config
from utils.prometheus import get_and_extract_all_metrics, get_and_extract_metric

router = APIRouter()

DISK_CONVERSION = {
    "bytes": 1,
    "kb": 1_000,
    "mb": 1_000_000,
    "gb": 1_000_000_000,
    "tb": 1_000_000_000_000
}

@router.get("/metrics/disk/free", tags=["disk"])
async def get_all_disks_free_metrics(format: str = "bytes"):
    return await handle_api_response(
        all_disk_metric,
        get_config("PROMETHEUS_URL"),
        "disk_free",
        "device",
        format
    )

@router.get("/metrics/disk/used", tags=["disk"])
async def get_all_disks_used_metrics(format: str = "bytes"):
    return await handle_api_response(
        all_disk_metric,
        get_config("PROMETHEUS_URL"),
        "disk_used",
        "device",
        format
    )

@router.get("/metrics/disk/total", tags=["disk"])
async def get_all_disks_total_metrics(format: str = "bytes"):
    return await handle_api_response(
        all_disk_metric,
        get_config("PROMETHEUS_URL"),
        "disk_total",
        "device",
        format
    )

@router.get("/metrics/disk/free/{disk_name}", tags=["disk"])
async def get_disk_free_metrics(disk_name: str, format: str = "bytes"):
    return await handle_api_response(
        single_disk_metric,
        get_config("PROMETHEUS_URL"),
        "disk_free",
        "device",
        disk_name,
        format
    )

@router.get("/metrics/disk/used/{disk_name}", tags=["disk"])
async def get_disk_used_metrics(disk_name: str, format: str = "bytes"):
    return await handle_api_response(
        single_disk_metric,
        get_config("PROMETHEUS_URL"),
        "disk_used",
        "device",
        disk_name,
        format
    )

@router.get("/metrics/disk/total/{disk_name}", tags=["disk"])
async def get_disk_total_metrics(disk_name: str, format: str = "bytes"):
    return await handle_api_response(
        single_disk_metric,
        get_config("PROMETHEUS_URL"),
        "disk_total",
        "device",
        disk_name,
        format
    )

@router.get("/usage/disk", tags=["disk"])
async def get_disks_usage():
    return await handle_api_response(
        get_and_extract_all_metrics,
        get_config("PROMETHEUS_URL"),
        f"disk_used_percent",
        "device"
    )

async def single_disk_metric(
        prometheus_url: str,
        promql_query: str,
        metric_key: str,
        disk_name: str,
        format: str = "bytes"
    ):
    result = await get_and_extract_metric(
        prometheus_url,
        promql_query,
        metric_key,
        disk_name
    )

    return str(float(result) / DISK_CONVERSION[format])

async def all_disk_metric(
        prometheus_url: str,
        promql_query: str,
        metric_key: str,
        format: str = "bytes"
    ):
    results = await get_and_extract_all_metrics(
        prometheus_url,
        promql_query,
        metric_key
    )

    for key, value in results.items():
        results[key] = str(float(value) / DISK_CONVERSION[format])
    
    return results
