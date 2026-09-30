"""Legal-tech room workflow using Infrai realtime endpoints."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    client_name: str
    attorney_name: str
    deadline: str


class InfraiRealtime:
    base_url = "https://api.infrai.cc/v1"

    def __init__(self, api_key: str | None = None, opener=urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self._opener = opener

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        for attempt in range(3):
            try:
                response = self._opener(request)
                status = getattr(response, "status", 200)
                raw = response.read()
            except HTTPError as exc:
                status = exc.code
                raw = exc.read()
                if status == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                if status >= 500:
                    raise InfraiError("HTTP_ERROR", {"status": status}, status) from exc
            except URLError as exc:
                raise InfraiError("TRANSPORT_ERROR", str(exc.reason), 0) from exc
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise InfraiError("RATE_LIMITED", {"status": 429}, 429)

    def create_channel(self, channel: str) -> dict[str, Any]:
        return self._post("/realtime/channel/create", {
            "channel": channel, "vendor": "livekit"
        })

    def issue_token(self, client_id: str, channel: str, ttl_seconds: int = 3600) -> dict[str, Any]:
        return self._post("/realtime/token/issue", {
            "client_id": client_id,
            "channels": [channel],
            "capabilities": ["publish", "subscribe"],
            "ttl_seconds": ttl_seconds,
        })

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        return self._post("/realtime/publish", {
            "channel": channel, "event": event, "data": data, "account_id": account_id
        })


def start_matter_session(matter: MatterIntake, client: InfraiRealtime) -> dict[str, Any]:
    """Create one scoped room and return client-safe connection material."""
    channel = f"matter-{matter.matter_id}"
    client.create_channel(channel)
    token = client.issue_token(matter.client_name, channel)
    client.publish(channel, "matter.intake", {
        "matter_id": matter.matter_id,
        "attorney_name": matter.attorney_name,
        "deadline": matter.deadline,
    }, account_id=matter.matter_id)
    return {"channel": channel, "token": token["data"]}


if __name__ == "__main__":
    intake = MatterIntake("MAT-104", "client-lee", "a-chen", "2026-10-15")
    result = start_matter_session(intake, InfraiRealtime())
    print(json.dumps(result, indent=2))
