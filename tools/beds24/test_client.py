import auth
from client import Beds24Client


class FakeResp:
    def __init__(self, payload, headers=None):
        self._payload = payload
        self.headers = headers or {}
        self.status_code = 200

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


class FakeHttp:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append({"url": url, "headers": headers or {}, "params": params or {}})
        return self._responses.pop(0)


def test_get_properties_sends_token_and_returns_data():
    http = FakeHttp([FakeResp({"success": True, "data": [{"id": 1, "name": "Casa"}]})])
    c = Beds24Client("acc", http=http)
    data = c.get_properties()
    assert data == [{"id": 1, "name": "Casa"}]
    assert http.calls[0]["headers"]["token"] == "acc"
    assert http.calls[0]["url"].endswith("/properties")


def test_get_bookings_follows_pages():
    # pagina 1 diz que ha proxima pagina (formato real: pages e um objeto); pagina 2 fecha
    http = FakeHttp([
        FakeResp({"success": True,
                  "pages": {"nextPageExists": True, "nextPageLink": "x"},
                  "data": [{"id": 10}, {"id": 11}]}),
        FakeResp({"success": True,
                  "pages": {"nextPageExists": False, "nextPageLink": None},
                  "data": [{"id": 12}]}),
    ])
    c = Beds24Client("acc", http=http)
    got = c.get_bookings(propertyId=1)
    assert [b["id"] for b in got] == [10, 11, 12]
    assert http.calls[0]["params"]["page"] == 1
    assert http.calls[1]["params"]["page"] == 2


def test_get_bookings_stops_when_page_empty():
    http = FakeHttp([
        FakeResp({"success": True, "data": [{"id": 10}]}),
        FakeResp({"success": True, "data": []}),
    ])
    c = Beds24Client("acc", http=http)
    got = c.get_bookings()
    assert [b["id"] for b in got] == [10]


def test_rate_limit_sleeps_when_exhausted():
    slept = []
    http = FakeHttp([
        FakeResp({"success": True, "data": [{"id": 1}]},
                 headers={"x-five-min-limit-remaining": "0", "x-five-min-limit-resets-in": "2"}),
        FakeResp({"success": True, "data": []}),
    ])
    c = Beds24Client("acc", http=http, sleep=lambda s: slept.append(s))
    c.get_bookings()
    assert slept == [2]
