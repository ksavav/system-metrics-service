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

async def get_and_extract_metric(
        prometheus_url: str,
        promql_query: str,
        metric_key: str,
        metric_name: str
    ) -> str:
    """
    Combines the process of querying Prometheus and extracting a specific metric value.
    """
    response = await get_prometheus_metrics(prometheus_url, promql_query)
    return extract_metric_value(response, metric_key, metric_name)

async def get_and_extract_all_metrics(prometheus_url: str, promql_query: str, key: str) -> dict:
    """
    Combines the process of querying Prometheus and extracting all metric values for a specific key.
    """
    response = await get_prometheus_metrics(prometheus_url, promql_query)
    data = response.get("data", {}).get("result", [])
    return {
        item.get("metric", {}).get(key): item.get("value", [None, None])[1]
        for item in data
    }
