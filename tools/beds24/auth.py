import requests

BASE_URL = "https://api.beds24.com/v2"


def load_beds24_env(path=".beds24auth"):
    env = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k] = v
    except FileNotFoundError:
        pass
    return env


def _write_env(path, env):
    with open(path, "w", encoding="utf-8") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")


def bootstrap_from_invite(code, http=requests, path=".beds24auth"):
    resp = http.get(
        f"{BASE_URL}/authentication/setup",
        headers={"code": code},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    env = load_beds24_env(path)
    env["BEDS24_REFRESH_TOKEN"] = data["refreshToken"]
    _write_env(path, env)
    return data


def get_access_token(http=requests, path=".beds24auth"):
    env = load_beds24_env(path)
    refresh = env["BEDS24_REFRESH_TOKEN"]
    resp = http.get(
        f"{BASE_URL}/authentication/token",
        headers={"refreshToken": refresh},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["token"]
