import httpx
from fastapi import HTTPException
from fastapi.responses import JSONResponse


async def async_http_request(url: str, method: str = "GET", json: dict = None, **kwargs) -> dict:
    """
    Makes an asynchronous HTTP request using httpx and returns the JSON response.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                json=json,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while making the request: {e}"
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"HTTP error occurred: {e.response.text}"
            )

async def handle_api_response(api_func: callable, *args, **kwargs) -> JSONResponse:
    """
    Handles the API response by calling the provided asynchronous function and returning a standardized JSON response.
    """
    try:
        data = await api_func(*args, **kwargs)
        return JSONResponse(
            status_code=200,
            content={"status": "success", "data": data}
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"status": "error", "detail": str(e.detail)}
        )
