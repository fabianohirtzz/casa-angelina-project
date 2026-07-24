import time
import requests
from auth import BASE_URL


class Beds24Client:
    def __init__(self, token, http=requests, sleep=time.sleep):
        self.token = token
        self.http = http
        self.sleep = sleep

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
            p = dict(params)
            p["page"] = page
            resp = self.http.get(f"{BASE_URL}/bookings", headers=self._headers(),
                                 params=p, timeout=60)
            resp.raise_for_status()
            body = resp.json()
            data = body.get("data", [])
            out.extend(data)
            self._respect_rate_limit(resp)
            pages = body.get("pages")
            if pages is not None:
                if page >= int(pages):
                    break
            elif not data:
                break
            if not data:
                break
            page += 1
        return out
