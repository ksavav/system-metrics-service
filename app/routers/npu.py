from statistics import mean

from fastapi import APIRouter

from utils.prometheus import get_and_extract_all_metrics, get_and_extract_metric
from utils.async_http import handle_api_response
from utils.config import get_config

router = APIRouter()

@router.get("/metrics/npu", tags=["npu"])
async def get_all_npu_utilization_metrics():
    return await handle_api_response(
        get_and_extract_all_metrics,
        get_config("PROMETHEUS_URL"),
        "npu_usage_percent",
        "accel_id"
    )

@router.get("/metrics/npu/{accel}", tags=["npu"])
async def get_single_npu_utilization_metric(accel: str):
    return await handle_api_response(
        get_and_extract_metric,
        get_config("PROMETHEUS_URL"),
        "npu_usage_percent",
        "accel_id",
        accel
    )

@router.get("/usage/npu", tags=["npu"])
async def get_npu_usage():
    return await handle_api_response(
        npu_usage,
        get_config("PROMETHEUS_URL"),
        "npu_usage_percent",
        "accel_id"
    )

async def npu_usage(prometheus_url: str, promql_query: str, key: str):
    usage = await get_and_extract_all_metrics(
        prometheus_url,
        promql_query,
        key,
    )
    return str(mean([float(u) for u in usage.values()]))
