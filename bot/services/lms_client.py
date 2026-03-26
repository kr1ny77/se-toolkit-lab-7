import httpx

from config import config


class BackendError(Exception):
    pass


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {config.lms_api_key}",
        "Content-Type": "application/json",
    }


def _handle_response(response: httpx.Response):
    response.raise_for_status()
    return response.json()


def _get(path: str, params: dict | None = None):
    url = f"{config.lms_api_base_url}{path}"
    try:
        response = httpx.get(url, headers=_headers(), params=params, timeout=20.0)
        return _handle_response(response)
    except httpx.HTTPStatusError as exc:
        raise BackendError(f"Backend error: HTTP {exc.response.status_code} {exc.response.reason_phrase}") from exc
    except httpx.ConnectError as exc:
        raise BackendError(f"Backend error: connection failed: {exc}") from exc
    except httpx.TimeoutException as exc:
        raise BackendError(f"Backend error: timeout: {exc}") from exc
    except httpx.HTTPError as exc:
        raise BackendError(f"Backend error: {exc}") from exc


def _post(path: str, payload: dict | None = None):
    url = f"{config.lms_api_base_url}{path}"
    try:
        response = httpx.post(url, headers=_headers(), json=payload or {}, timeout=30.0)
        return _handle_response(response)
    except httpx.HTTPStatusError as exc:
        raise BackendError(f"Backend error: HTTP {exc.response.status_code} {exc.response.reason_phrase}") from exc
    except httpx.ConnectError as exc:
        raise BackendError(f"Backend error: connection failed: {exc}") from exc
    except httpx.TimeoutException as exc:
        raise BackendError(f"Backend error: timeout: {exc}") from exc
    except httpx.HTTPError as exc:
        raise BackendError(f"Backend error: {exc}") from exc


def get_items():
    return _get("/items/")


def get_learners():
    return _get("/learners/")


def get_scores(lab: str):
    return _get("/analytics/scores", {"lab": lab})


def get_pass_rates(lab: str):
    return _get("/analytics/pass-rates", {"lab": lab})


def get_timeline(lab: str):
    return _get("/analytics/timeline", {"lab": lab})


def get_groups(lab: str):
    return _get("/analytics/groups", {"lab": lab})


def get_top_learners(lab: str | None = None, limit: int = 5):
    params = {"limit": limit}
    if lab:
        params["lab"] = lab
    return _get("/analytics/top-learners", params)


def get_completion_rate(lab: str):
    return _get("/analytics/completion-rate", {"lab": lab})


def trigger_sync():
    return _post("/pipeline/sync", {})
