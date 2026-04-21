import httpx


async def async_http_request(url: str, method: str = "GET", json: dict = None, **kwargs):
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
            print(f"An error occurred while making the request: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
