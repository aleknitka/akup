from __future__ import annotations

import httpx
from rich.console import Console

from cli.config import get_api_key, get_api_url

console = Console()


class AkupClient:
    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        headers: dict[str, str] = {}
        if api_key:
            headers["X-API-Key"] = api_key
        self._client = httpx.Client(base_url=base_url, headers=headers, timeout=30.0)

    def _handle_response(self, resp: httpx.Response) -> httpx.Response:
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            console.print(f"[red]Error {resp.status_code}:[/red] {detail}")
            raise SystemExit(1)
        return resp

    def get(self, path: str, **kwargs: object) -> httpx.Response:
        return self._handle_response(self._client.get(path, **kwargs))

    def post(self, path: str, **kwargs: object) -> httpx.Response:
        return self._handle_response(self._client.post(path, **kwargs))

    def put(self, path: str, **kwargs: object) -> httpx.Response:
        return self._handle_response(self._client.put(path, **kwargs))

    def delete(self, path: str, **kwargs: object) -> httpx.Response:
        return self._handle_response(self._client.delete(path, **kwargs))


def get_client(require_auth: bool = True) -> AkupClient:
    url = get_api_url()
    key = get_api_key() if require_auth else None
    return AkupClient(base_url=url, api_key=key)
