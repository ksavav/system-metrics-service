from fastapi import APIRouter

from utils.async_http import handle_api_response
from utils.config import get_config
from utils.prometheus import get_prometheus_metrics

router = APIRouter()

@router.get("/metrics/disk/free/{disk_name}", tags=["disk"])
async def get_disk_free_metrics(disk_name: str):
    """
    Queries Prometheus for the disk free space system metric.
    """
    return await handle_api_response(
        get_prometheus_metrics,
        get_config("PROMETHEUS_URL"),
        f"disk_free{{disk='{disk_name}'}}"
    )

# disk_total
# disk_used
# disk_free
# disk_used_percent
