from statistics import mean

from fastapi import HTTPException

from .async_http import async_http_request


async def get_prometheus_metrics(prometheus_url: str, promql_query: str) -> dict:
    """
    Queries Prometheus for the specified metric using the provided PromQL query.
    """
    url = f"{prometheus_url}/api/v1/query"
    params = {"query": promql_query}

    response = await async_http_request(url=url, method="GET", params=params)

    if response.get("status") != "success":
        raise HTTPException(status_code=500, detail="Prometheus query failed")

    return response

def extract_metric_value(metric_data: dict, metric_key: str, metric_name: str) -> str:
    """
    Extracts the value of a specific metric from the Prometheus response data.
    """
    data = metric_data.get("data", {}).get("result", [])
    return next(
        (
            item.get("value", [None, None])[1] for item in data if
            item.get("metric", {}).get(metric_key) == metric_name),
        None
    )

# CPU Metrics
async def cpu_total_usage(prometheus_url: str) -> str:
    """
    Queries Prometheus for the current CPU usage system metric.
    """
    promql_query = 'cpu_usage_system'
    response = await get_prometheus_metrics(prometheus_url, promql_query)

    return extract_metric_value(response, "cpu", "cpu-total")

# GPU Metrics
async def gpu_memory_metrcis(prometheus_url: str) -> dict:
    """
    Queries Prometheus for the current GPU memory system metric.
    """
    free = await get_prometheus_metrics(prometheus_url, "nvidia_smi_memory_free")
    used = await get_prometheus_metrics(prometheus_url, "nvidia_smi_memory_used")
    total = await get_prometheus_metrics(prometheus_url, "nvidia_smi_memory_total")
    return {
        "free": free.get("data", {}).get("result", []),
        "used": used.get("data", {}).get("result", []),
        "total": total.get("data", {}).get("result", [])
    }

async def gpu_total_usage(prometheus_url: str) -> str:
    """
    Queries Prometheus for the current GPU usage system metric.
    """
    promql_query = 'nvidia_smi_utilization_gpu'
    response = await get_prometheus_metrics(prometheus_url, promql_query)
    return str(mean(
        float(item.get("value", [None, None])[1])
        for item in response.get("data", {}).get("result", [])
    ))

async def gpu_memory_usage(prometheus_url: str) -> str:
    """
    Queries Prometheus for the current GPU memory system metric.
    """
    promql_query = 'nvidia_smi_utilization_memory'
    response = await get_prometheus_metrics(prometheus_url, promql_query)
    return str(mean(
        float(item.get("value", [None, None])[1])
        for item in response.get("data", {}).get("result", [])
    ))

# NPU Metrics
# Memory Metrics
# Disk Metrics
