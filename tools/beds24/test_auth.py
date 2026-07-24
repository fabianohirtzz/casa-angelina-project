import json
import auth


class FakeResp:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status
        self.headers = {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeHttp:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append({"url": url, "headers": headers or {}})
        return FakeResp(self.payload)


def test_bootstrap_writes_refresh_token(tmp_path):
    path = tmp_path / ".beds24auth"
    http = FakeHttp({"token": "acc1", "refreshToken": "ref1", "expiresIn": 86400})
    out = auth.bootstrap_from_invite("INVITE123", http=http, path=str(path))
    assert out["refreshToken"] == "ref1"
    assert http.calls[0]["headers"]["code"] == "INVITE123"
    assert http.calls[0]["url"].endswith("/authentication/setup")
    saved = auth.load_beds24_env(str(path))
    assert saved["BEDS24_REFRESH_TOKEN"] == "ref1"


def test_get_access_token_uses_refresh(tmp_path):
    path = tmp_path / ".beds24auth"
    path.write_text("BEDS24_REFRESH_TOKEN=ref1\n", encoding="utf-8")
    http = FakeHttp({"token": "acc2", "expiresIn": 86400})
    tok = auth.get_access_token(http=http, path=str(path))
    assert tok == "acc2"
    assert http.calls[0]["headers"]["refreshToken"] == "ref1"
    assert http.calls[0]["url"].endswith("/authentication/token")
