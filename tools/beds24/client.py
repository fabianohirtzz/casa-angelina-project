import time
import requests
from auth import BASE_URL


class Beds24Client:
    def __init__(self, token, http=requests, sleep=time.sleep, max_pages=1000):
        self.token = token
        self.http = http
        self.sleep = sleep
        self.max_pages = max_pages

    def _headers(self):
        return {"token": self.token}

    def _respect_rate_limit(self, resp):
        rem = resp.headers.get("x-five-min-limit-remaining")
        if rem is not None and str(rem) == "0":
            wait = int(resp.headers.get("x-five-min-limit-resets-in", "5"))
            self.sleep(wait)

    def get_properties(self, **params):
        p = {"includeAllRooms": "true"}
        p.update(params)
        resp = self.http.get(f"{BASE_URL}/properties", headers=self._headers(),
                             params=p, timeout=60)
        resp.raise_for_status()
        self._respect_rate_limit(resp)
        return resp.json().get("data", [])

    def get_bookings(self, **params):
        out = []
        page = 1
        while True:
            if page > self.max_pages:
                raise RuntimeError(
                    f"Beds24 get_bookings excedeu max_pages={self.max_pages} "
                    "(possivel loop de paginacao)"
                )
            p = dict(params)
            p["page"] = page
            resp = self.http.get(f"{BASE_URL}/bookings", headers=self._headers(),
                                 params=p, timeout=60)
            resp.raise_for_status()
            body = resp.json()
            data = body.get("data", [])
            out.extend(data)
            self._respect_rate_limit(resp)
            if not data:
                break
            pages = body.get("pages")
            next_exists = bool(pages.get("nextPageExists")) if isinstance(pages, dict) else False
            if not next_exists:
                break
            page += 1
        return out
