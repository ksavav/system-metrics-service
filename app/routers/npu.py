from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config

router = APIRouter()

@router.get("/metrics/npu/utilization", tags=["npu"])
async def get_npu_utilization_metrics():
    raise NotImplementedError("NPU metrics are not implemented yet.")
    return await handle_api_response(
        get_config("PROMETHEUS_URL"),
        "npu_utilization"
    )
