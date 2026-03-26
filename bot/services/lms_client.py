import httpx

from config import config


class BackendError(Exception):
    """User-friendly backend error for handlers."""


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {config.lms_api_key}",
        "Content-Type": "application/json",
    }


def _format_http_error(response: httpx.Response) -> str:
    return f"Backend error: HTTP {response.status_code} {response.reason_phrase}. The backend service may be down."


def _format_connect_error(exc: Exception) -> str:
    return f"Backend error: {str(exc)}. Check that the services are running."


def get_items() -> list[dict]:
    url = f"{config.lms_api_base_url}/items/"
    try:
        response = httpx.get(url, headers=_headers(), timeout=10.0)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise BackendError("Backend error: unexpected /items response format.")
        return data
    except httpx.HTTPStatusError as exc:
        raise BackendError(_format_http_error(exc.response)) from exc
    except httpx.ConnectError as exc:
        raise BackendError(_format_connect_error(exc)) from exc
    except httpx.TimeoutException as exc:
        raise BackendError(f"Backend error: request timed out. {exc}") from exc
    except httpx.HTTPError as exc:
        raise BackendError(f"Backend error: {exc}") from exc


def get_pass_rates(lab_id: str) -> list[dict]:
    url = f"{config.lms_api_base_url}/analytics/pass-rates"
    try:
        response = httpx.get(
            url,
            headers=_headers(),
            params={"lab": lab_id},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise BackendError("Backend error: unexpected /analytics/pass-rates response format.")
        return data
    except httpx.HTTPStatusError as exc:
        raise BackendError(_format_http_error(exc.response)) from exc
    except httpx.ConnectError as exc:
        raise BackendError(_format_connect_error(exc)) from exc
    except httpx.TimeoutException as exc:
        raise BackendError(f"Backend error: request timed out. {exc}") from exc
    except httpx.HTTPError as exc:
        raise BackendError(f"Backend error: {exc}") from exc
