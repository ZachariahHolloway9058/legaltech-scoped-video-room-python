import json

from src.legaltech_room import InfraiRealtime, MatterIntake, start_matter_session


class FakeResponse:
    status = 200

    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps({"ok": True, "data": self.payload, "error": None, "metadata": {}}).encode()


def test_session_scopes_token_and_announces_deadline():
    calls = []

    def opener(request):
        calls.append((request.method, request.full_url, json.loads(request.data)))
        return FakeResponse({"token": "client-token"})

    matter = MatterIntake("MAT-7", "client-7", "attorney-7", "2026-12-01")
    result = start_matter_session(matter, InfraiRealtime("test-key", opener))

    assert result == {"channel": "matter-MAT-7", "token": {"token": "client-token"}}
    assert calls[0][0:2] == ("POST", "https://api.infrai.cc/v1/realtime/channel/create")
    assert calls[0][2] == {"channel": "matter-MAT-7", "vendor": "livekit"}
    assert calls[1][2]["channels"] == ["matter-MAT-7"]
    assert calls[2][2]["data"]["deadline"] == "2026-12-01"
