# Painel — Plano 2a: Seed + Backfill Beds24 (local) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Espelhar o Beds24 → Supabase (`casa_angelina.*`) por um script Python local: seed da propriedade + 4 quartos e backfill idempotente das reservas, provado por testes.

**Architecture:** Módulos Python em `tools/beds24/` reusando o harness de banco do Plano 1 (conexão direta ao Postgres como superuser, fura o RLS — correto para backfill de backend). Camadas isoladas: auth (Beds24), client HTTP, mapeamento puro (Beds24 → nossas linhas), upsert idempotente, seed, e orquestração do backfill. Tasks 1–6 são construídas e testadas **offline** (HTTP mockado; DB real onde precisa). Só a Task 7 usa o token real do Beds24.

**Tech Stack:** Python 3.12 + `requests` + `psycopg2-binary` + `pytest`. PostgreSQL 17 (Supabase). Beds24 API v2.

## Global Constraints

- **Schema alvo:** `casa_angelina`. NUNCA tocar em `public` (é do HD360).
- **Backfill fura o RLS de propósito** (conexão superuser via `SUPABASE_DB_URL`); a `service_role` REST key não é usada nesta fatia (fica para as Edge Functions do Plano 2b).
- **Segredos:** refresh token do Beds24 só em `.beds24auth` (gitignored, novo arquivo, mesmo padrão do `.supabaseauth`). Credenciais do banco só em `.supabaseauth`. NUNCA no git nem em código commitado.
- **Idempotência:** seed e backfill re-executáveis. Upsert de reserva casa por `beds24_booking_id`; só atualiza se `modifiedTime` do payload for mais novo que o `beds24_modified_at` gravado. Cancelamento vira `status='cancelled'` (não deleta).
- **Mapa de status (case-insensitive):** `new`/`confirmed`→`confirmed`; `request`/`inquiry`→`pending`; `cancelled`→`cancelled`; `black`→linha em `calendar_blocks` (`source='beds24'`), não reserva.
- **Mapa de canal:** `apiSourceId` 0→`direct`, 19→`booking`, 46→`airbnb`; qualquer outro→`manual`.
- **`masterId`→`group_ref`**; booking id (um por quarto)→`beds24_booking_id`; `roomId`→resolve `room_id` por `rooms.beds24_room_id`.
- **Quartos canônicos** (nomes e capacidades, ver memória `casa-angelina-quartos`): Quarto Duplo com Varanda (2), Quarto Triplo com Vista para a Piscina (3), Quarto Superior com Cama King-size 1 (2), Quarto Superior com Cama King-size 2 (2).
- **Campos da API não 100% confirmados na doc pública** (ver `docs/superpowers/references/beds24-api-v2-research.md`): nomes de campos de data/ocupação, shape do envelope de paginação, casing de status e valores de `apiSourceId`. A Task 7 (probe, com token real) confirma tudo antes do backfill definitivo; o mapeamento é escrito contra os nomes documentados do Beds24 v2 e tolera divergência falhando alto.

## File Structure

- `tools/beds24/requirements.txt` — `requests`, `psycopg2-binary`, `pytest`.
- `tools/beds24/auth.py` — invite code → refresh token → access token; lê/grava `.beds24auth`.
- `tools/beds24/client.py` — `Beds24Client`: `get_properties()`, `get_bookings()` (paginação + rate-limit).
- `tools/beds24/mapping.py` — funções puras Beds24 → dict de colunas (sem rede, sem DB).
- `tools/beds24/upsert.py` — resolve room/guest e faz upsert idempotente (recebe cursor).
- `tools/beds24/seed.py` — seed data-driven da property + 4 rooms a partir do payload de properties.
- `tools/beds24/backfill.py` — orquestra seed → paginação → upsert → cursor em `sync_state`.
- `tools/beds24/db.py` — helper que reusa `db_url()` do Plano 1 e abre conexão (para os entrypoints).
- `tools/beds24/conftest.py` — fixture pytest `conn` (transação + rollback), reusando `db_url()`.
- `tools/beds24/test_auth.py`, `test_client.py`, `test_mapping.py`, `test_upsert.py`, `test_seed.py`, `test_backfill.py` — testes.
- `.beds24auth` — NOVO segredo local (gitignored). Adicionar ao `.gitignore`.

---

### Task 1: Auth do Beds24 + `.beds24auth` gitignored

**Files:**
- Create: `tools/beds24/requirements.txt`
- Create: `tools/beds24/auth.py`
- Modify: `.gitignore` (adicionar `.beds24auth`)
- Test: `tools/beds24/test_auth.py`

**Interfaces:**
- Produces: `BASE_URL = "https://api.beds24.com/v2"`; `load_beds24_env(path=".beds24auth") -> dict`; `bootstrap_from_invite(code, http=requests, path=".beds24auth") -> dict` (troca invite code por refresh token e o grava); `get_access_token(http=requests, path=".beds24auth") -> str` (usa o refresh token para obter access token). `http` é injetável para teste (objeto com `.get(url, headers=...)`).

- [ ] **Step 1: Criar `tools/beds24/requirements.txt`**

```
requests
psycopg2-binary
pytest
```

- [ ] **Step 2: Adicionar `.beds24auth` ao `.gitignore`**

Acrescentar uma linha `.beds24auth` ao arquivo `.gitignore` na raiz (perto de onde `.supabaseauth` já aparece). Não remover nenhuma linha existente.

- [ ] **Step 3: Escrever o teste `tools/beds24/test_auth.py`**

```python
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
```

- [ ] **Step 4: Rodar o teste (deve falhar — módulo não existe)**

Run: `python -m pytest tools/beds24/test_auth.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'auth'` ou `AttributeError`).

- [ ] **Step 5: Escrever `tools/beds24/auth.py`**

```python
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
```

- [ ] **Step 6: Rodar o teste (deve passar)**

Run: `python -m pytest tools/beds24/test_auth.py -v`
Expected: PASS (2 passed). Nota: os testes usam `tmp_path` e um HTTP fake; nenhuma rede é tocada.

- [ ] **Step 7: Commit**

```bash
git add tools/beds24/requirements.txt tools/beds24/auth.py tools/beds24/test_auth.py .gitignore
git commit -m "Painel 2a: auth do Beds24 (invite->refresh->access) + .beds24auth gitignored"
```

---

### Task 2: Cliente HTTP do Beds24 (properties + bookings paginado)

**Files:**
- Create: `tools/beds24/client.py`
- Test: `tools/beds24/test_client.py`

**Interfaces:**
- Consumes: `auth.BASE_URL`.
- Produces: `class Beds24Client(token, http=requests, sleep=time.sleep)` com `get_properties() -> list[dict]` (retorna `data`) e `get_bookings(**params) -> list[dict]` (segue paginação, retorna a lista achatada de bookings). Envia header `token: <token>` em toda chamada. Respeita rate-limit: se `x-five-min-limit-remaining` vier `0`, dorme `x-five-min-limit-resets-in` segundos antes de seguir.

- [ ] **Step 1: Escrever o teste `tools/beds24/test_client.py`**

```python
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
    # pagina 1 diz que ha 2 paginas; pagina 2 fecha
    http = FakeHttp([
        FakeResp({"success": True, "pages": 2, "data": [{"id": 10}, {"id": 11}]}),
        FakeResp({"success": True, "pages": 2, "data": [{"id": 12}]}),
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
```

- [ ] **Step 2: Rodar o teste (deve falhar)**

Run: `python -m pytest tools/beds24/test_client.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'client'`).

- [ ] **Step 3: Escrever `tools/beds24/client.py`**

```python
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
```

- [ ] **Step 4: Rodar o teste (deve passar)**

Run: `python -m pytest tools/beds24/test_client.py -v`
Expected: PASS (4 passed). Nenhuma rede tocada (HTTP fake).

- [ ] **Step 5: Commit**

```bash
git add tools/beds24/client.py tools/beds24/test_client.py
git commit -m "Painel 2a: cliente Beds24 (properties + bookings paginado + rate-limit)"
```

---

### Task 3: Mapeamento puro (Beds24 → nossas linhas) — o núcleo

**Files:**
- Create: `tools/beds24/mapping.py`
- Test: `tools/beds24/test_mapping.py`

**Interfaces:**
- Produces (funções puras, sem rede/DB):
  - `map_status(beds24_status) -> str | None` — retorna `'confirmed'|'pending'|'cancelled'` ou `None` se for bloqueio (`black`).
  - `is_block(beds24_status) -> bool`.
  - `map_channel(api_source_id) -> str` — `'direct'|'booking'|'airbnb'|'manual'`.
  - `map_booking_to_reservation(b, room_id, guest_id) -> dict` — dict com chaves das colunas de `reservations`.
  - `map_booking_to_block(b, room_id) -> dict` — dict com chaves de `calendar_blocks`.
  - `guest_fields(b) -> dict` — extrai `full_name/email/phone/country` do booking.

- [ ] **Step 1: Escrever o teste `tools/beds24/test_mapping.py`**

```python
import pytest
import mapping


def _booking(**over):
    b = {
        "id": 555,
        "propertyId": 1,
        "roomId": 99,
        "status": "confirmed",
        "arrival": "2026-02-10",
        "departure": "2026-02-14",
        "numAdult": 2,
        "numChild": 0,
        "firstName": "Ana",
        "lastName": "Silva",
        "email": "ana@x.com",
        "phone": "5573999",
        "country": "BR",
        "price": "1584.00",
        "apiSourceId": 19,
        "masterId": 555,
        "modifiedTime": "2026-01-20 10:00:00",
    }
    b.update(over)
    return b


def test_map_status_variants():
    assert mapping.map_status("New") == "confirmed"
    assert mapping.map_status("CONFIRMED") == "confirmed"
    assert mapping.map_status("Request") == "pending"
    assert mapping.map_status("inquiry") == "pending"
    assert mapping.map_status("Cancelled") == "cancelled"
    assert mapping.map_status("Black") is None


def test_is_block():
    assert mapping.is_block("black") is True
    assert mapping.is_block("Confirmed") is False


def test_map_channel():
    assert mapping.map_channel(0) == "direct"
    assert mapping.map_channel(19) == "booking"
    assert mapping.map_channel(46) == "airbnb"
    assert mapping.map_channel(123) == "manual"
    assert mapping.map_channel(None) == "manual"


def test_map_booking_to_reservation():
    row = mapping.map_booking_to_reservation(_booking(), room_id="R", guest_id="G")
    assert row["room_id"] == "R"
    assert row["guest_id"] == "G"
    assert row["beds24_booking_id"] == "555"
    assert row["group_ref"] == "555"
    assert row["channel"] == "booking"
    assert row["status"] == "confirmed"
    assert row["check_in"] == "2026-02-10"
    assert row["check_out"] == "2026-02-14"
    assert row["num_guests"] == 2
    assert str(row["total_amount"]) == "1584.00"
    assert row["beds24_modified_at"] == "2026-01-20 10:00:00"
    assert row["raw_payload"]["id"] == 555


def test_reservation_num_guests_sums_adults_and_children():
    row = mapping.map_booking_to_reservation(_booking(numAdult=2, numChild=1),
                                             room_id="R", guest_id=None)
    assert row["num_guests"] == 3
    assert row["guest_id"] is None


def test_map_booking_to_block():
    blk = mapping.map_booking_to_block(_booking(status="Black"), room_id="R")
    assert blk["room_id"] == "R"
    assert blk["start_date"] == "2026-02-10"
    assert blk["end_date"] == "2026-02-14"
    assert blk["source"] == "beds24"


def test_guest_fields():
    g = mapping.guest_fields(_booking())
    assert g["full_name"] == "Ana Silva"
    assert g["email"] == "ana@x.com"
    assert g["phone"] == "5573999"
    assert g["country"] == "BR"
```

- [ ] **Step 2: Rodar o teste (deve falhar)**

Run: `python -m pytest tools/beds24/test_mapping.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'mapping'`).

- [ ] **Step 3: Escrever `tools/beds24/mapping.py`**

```python
_STATUS = {
    "new": "confirmed",
    "confirmed": "confirmed",
    "request": "pending",
    "inquiry": "pending",
    "cancelled": "cancelled",
    "canceled": "cancelled",
}

_CHANNEL = {0: "direct", 19: "booking", 46: "airbnb"}


def _norm(status):
    return (status or "").strip().lower()


def is_block(beds24_status):
    return _norm(beds24_status) == "black"


def map_status(beds24_status):
    if is_block(beds24_status):
        return None
    s = _norm(beds24_status)
    if s not in _STATUS:
        raise ValueError(f"status Beds24 desconhecido: {beds24_status!r}")
    return _STATUS[s]


def map_channel(api_source_id):
    try:
        return _CHANNEL.get(int(api_source_id), "manual")
    except (TypeError, ValueError):
        return "manual"


def guest_fields(b):
    name = " ".join(x for x in [b.get("firstName"), b.get("lastName")] if x).strip()
    return {
        "full_name": name or None,
        "email": b.get("email"),
        "phone": b.get("phone") or b.get("mobile"),
        "country": b.get("country"),
    }


def _num_guests(b):
    total = (b.get("numAdult") or 0) + (b.get("numChild") or 0)
    return total or None


def map_booking_to_reservation(b, room_id, guest_id):
    return {
        "room_id": room_id,
        "guest_id": guest_id,
        "beds24_booking_id": str(b["id"]),
        "group_ref": str(b["masterId"]) if b.get("masterId") else None,
        "channel": map_channel(b.get("apiSourceId")),
        "status": map_status(b.get("status")),
        "check_in": b["arrival"],
        "check_out": b["departure"],
        "num_guests": _num_guests(b),
        "total_amount": b.get("price"),
        "beds24_modified_at": b.get("modifiedTime"),
        "raw_payload": b,
    }


def map_booking_to_block(b, room_id):
    return {
        "room_id": room_id,
        "start_date": b["arrival"],
        "end_date": b["departure"],
        "reason": "Beds24 block",
        "source": "beds24",
    }
```

- [ ] **Step 4: Rodar o teste (deve passar)**

Run: `python -m pytest tools/beds24/test_mapping.py -v`
Expected: PASS (7 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/beds24/mapping.py tools/beds24/test_mapping.py
git commit -m "Painel 2a: mapeamento puro Beds24 -> reservations/calendar_blocks"
```

---

### Task 4: Upsert idempotente (resolve room/guest, grava com guarda de modificação)

**Files:**
- Create: `tools/beds24/db.py`
- Create: `tools/beds24/conftest.py`
- Create: `tools/beds24/upsert.py`
- Test: `tools/beds24/test_upsert.py`

**Interfaces:**
- Consumes: `mapping.*`; fixture `conn`; schema do Plano 1.
- Produces:
  - `db.py`: `db_url()` (reusa o do harness) e `connect()` (nova conexão psycopg2).
  - `upsert.py`:
    - `resolve_room_id(cur, property_id, beds24_room_id) -> str | None`.
    - `resolve_or_create_guest(cur, property_id, booking) -> str | None`.
    - `upsert_reservation(cur, property_id, room_id, guest_id, booking) -> str | None` (aplica guarda de `beds24_modified_at`; retorna o id da reserva).
    - `upsert_block(cur, property_id, room_id, booking) -> None`.

- [ ] **Step 1: Criar `tools/beds24/db.py`** (reusa o `db_url` do Plano 1 sem duplicar segredo/lógica)

```python
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "db"))
from apply import db_url  # noqa: E402
import psycopg2  # noqa: E402


def connect():
    return psycopg2.connect(db_url(), connect_timeout=20)
```

- [ ] **Step 2: Criar a fixture `tools/beds24/conftest.py`**

```python
import pytest
from db import connect


@pytest.fixture
def conn():
    c = connect()
    try:
        yield c
    finally:
        c.rollback()
        c.close()
```

- [ ] **Step 3: Escrever o teste `tools/beds24/test_upsert.py`**

```python
import upsert


def _prop_room(cur):
    cur.execute(
        "insert into casa_angelina.properties (beds24_property_id,name,slug) "
        "values ('u-prop','U','u-slug') returning id"
    )
    pid = cur.fetchone()[0]
    cur.execute(
        "insert into casa_angelina.rooms (property_id,beds24_room_id,name,slug,capacity) "
        "values (%s,'u-room','R','r',2) returning id",
        (pid,),
    )
    rid = cur.fetchone()[0]
    return pid, rid


def _booking(**over):
    b = {
        "id": 700, "propertyId": 1, "roomId": "u-room", "status": "confirmed",
        "arrival": "2026-03-01", "departure": "2026-03-05", "numAdult": 2, "numChild": 0,
        "firstName": "Ana", "lastName": "Silva", "email": "ana@x.com", "phone": "55",
        "country": "BR", "price": "800.00", "apiSourceId": 19, "masterId": 700,
        "modifiedTime": "2026-02-01 10:00:00",
    }
    b.update(over)
    return b


def test_resolve_room_id(conn):
    with conn.cursor() as cur:
        pid, rid = _prop_room(cur)
        assert upsert.resolve_room_id(cur, pid, "u-room") == rid
        assert upsert.resolve_room_id(cur, pid, "nope") is None


def test_resolve_or_create_guest_is_idempotent(conn):
    with conn.cursor() as cur:
        pid, rid = _prop_room(cur)
        g1 = upsert.resolve_or_create_guest(cur, pid, _booking())
        g2 = upsert.resolve_or_create_guest(cur, pid, _booking())
        assert g1 == g2  # mesmo email/phone => nao duplica


def test_upsert_reservation_inserts_then_updates_only_if_newer(conn):
    with conn.cursor() as cur:
        pid, rid = _prop_room(cur)
        gid = upsert.resolve_or_create_guest(cur, pid, _booking())
        rid1 = upsert.upsert_reservation(cur, pid, rid, gid, _booking(price="800.00"))
        # reenvio com modificacao MAIS ANTIGA e preco diferente => ignora
        upsert.upsert_reservation(cur, pid, rid, gid,
                                  _booking(price="999.00", modifiedTime="2026-01-01 00:00:00"))
        cur.execute("select total_amount from casa_angelina.reservations where id=%s", (rid1,))
        assert str(cur.fetchone()[0]) == "800.00"
        # reenvio com modificacao MAIS NOVA => atualiza
        upsert.upsert_reservation(cur, pid, rid, gid,
                                  _booking(price="777.00", modifiedTime="2026-02-02 10:00:00"))
        cur.execute("select count(*) from casa_angelina.reservations where beds24_booking_id='700'")
        assert cur.fetchone()[0] == 1  # nao duplicou
        cur.execute("select total_amount from casa_angelina.reservations where id=%s", (rid1,))
        assert str(cur.fetchone()[0]) == "777.00"


def test_upsert_block_inserts_calendar_block(conn):
    with conn.cursor() as cur:
        pid, rid = _prop_room(cur)
        upsert.upsert_block(cur, pid, rid, _booking(status="Black"))
        cur.execute("select count(*) from casa_angelina.calendar_blocks "
                    "where room_id=%s and source='beds24'", (rid,))
        assert cur.fetchone()[0] == 1
```

- [ ] **Step 4: Rodar o teste (deve falhar)**

Run: `python -m pytest tools/beds24/test_upsert.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'upsert'`).

- [ ] **Step 5: Escrever `tools/beds24/upsert.py`**

```python
import json
import mapping


def resolve_room_id(cur, property_id, beds24_room_id):
    cur.execute(
        "select id from casa_angelina.rooms where property_id=%s and beds24_room_id=%s",
        (property_id, str(beds24_room_id)),
    )
    row = cur.fetchone()
    return row[0] if row else None


def resolve_or_create_guest(cur, property_id, booking):
    g = mapping.guest_fields(booking)
    if g["email"]:
        cur.execute(
            "select id from casa_angelina.guests where property_id=%s and email=%s",
            (property_id, g["email"]),
        )
        row = cur.fetchone()
        if row:
            return row[0]
    if g["phone"]:
        cur.execute(
            "select id from casa_angelina.guests where property_id=%s and phone=%s",
            (property_id, g["phone"]),
        )
        row = cur.fetchone()
        if row:
            return row[0]
    if not any([g["full_name"], g["email"], g["phone"]]):
        return None
    cur.execute(
        "insert into casa_angelina.guests (property_id,full_name,email,phone,country) "
        "values (%s,%s,%s,%s,%s) returning id",
        (property_id, g["full_name"], g["email"], g["phone"], g["country"]),
    )
    return cur.fetchone()[0]


def upsert_reservation(cur, property_id, room_id, guest_id, booking):
    row = mapping.map_booking_to_reservation(booking, room_id, guest_id)
    cur.execute(
        "select id, beds24_modified_at from casa_angelina.reservations "
        "where beds24_booking_id=%s and room_id=%s",
        (row["beds24_booking_id"], room_id),
    )
    existing = cur.fetchone()
    payload = json.dumps(row["raw_payload"])
    if existing:
        res_id = existing[0]
        new_mod = row["beds24_modified_at"]
        # guarda de idempotencia FEITA EM SQL (compara timestamptz, nao string):
        # so atualiza se o gravado for null ou mais antigo que o modifiedTime do payload.
        cur.execute(
            "update casa_angelina.reservations set "
            "guest_id=%s, group_ref=%s, channel=%s, status=%s, check_in=%s, check_out=%s, "
            "num_guests=%s, total_amount=%s, beds24_modified_at=%s, raw_payload=%s, "
            "synced_at=now(), updated_at=now() "
            "where id=%s and (beds24_modified_at is null or beds24_modified_at < %s::timestamptz)",
            (guest_id, row["group_ref"], row["channel"], row["status"], row["check_in"],
             row["check_out"], row["num_guests"], row["total_amount"],
             row["beds24_modified_at"], payload, res_id, new_mod),
        )
        return res_id
    cur.execute(
        "insert into casa_angelina.reservations "
        "(property_id,room_id,guest_id,beds24_booking_id,group_ref,channel,status,"
        "check_in,check_out,num_guests,total_amount,raw_payload,beds24_modified_at,synced_at) "
        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now()) returning id",
        (property_id, room_id, guest_id, row["beds24_booking_id"], row["group_ref"],
         row["channel"], row["status"], row["check_in"], row["check_out"],
         row["num_guests"], row["total_amount"], payload, row["beds24_modified_at"]),
    )
    return cur.fetchone()[0]


def upsert_block(cur, property_id, room_id, booking):
    blk = mapping.map_booking_to_block(booking, room_id)
    cur.execute(
        "select id from casa_angelina.calendar_blocks "
        "where room_id=%s and start_date=%s and end_date=%s and source='beds24'",
        (room_id, blk["start_date"], blk["end_date"]),
    )
    if cur.fetchone():
        return
    cur.execute(
        "insert into casa_angelina.calendar_blocks "
        "(property_id,room_id,start_date,end_date,reason,source) "
        "values (%s,%s,%s,%s,%s,'beds24')",
        (property_id, room_id, blk["start_date"], blk["end_date"], blk["reason"]),
    )
```

- [ ] **Step 6: Rodar os testes (devem passar)**

Run: `python -m pytest tools/beds24/test_upsert.py -v`
Expected: PASS (4 passed). Usam o banco real via fixture `conn`; tudo revertido no rollback.

- [ ] **Step 7: Commit**

```bash
git add tools/beds24/db.py tools/beds24/conftest.py tools/beds24/upsert.py tools/beds24/test_upsert.py
git commit -m "Painel 2a: upsert idempotente (resolve room/guest + guarda de modificacao)"
```

---

### Task 5: Seed data-driven (property + 4 rooms a partir do payload de properties)

**Files:**
- Create: `tools/beds24/seed.py`
- Test: `tools/beds24/test_seed.py`

**Interfaces:**
- Consumes: fixture `conn`; payload de `client.get_properties()`.
- Produces:
  - `CANONICAL_ROOMS` — lista de `{"slug","name","capacity","sort_order","match"}` dos 4 quartos.
  - `match_room(beds24_room_name) -> str | None` — retorna o slug canônico ou `None`.
  - `seed_property_and_rooms(cur, property_payload) -> dict` — upsert de 1 property + 4 rooms; retorna `{"property_id":..., "rooms_by_beds24_id": {beds24_room_id: room_id}}`. Levanta `ValueError` se algum roomType não casar com um quarto canônico.

- [ ] **Step 1: Escrever o teste `tools/beds24/test_seed.py`**

```python
import pytest
import seed


def _payload():
    return {
        "id": 4242,
        "name": "Casa Angelina",
        "roomTypes": [
            {"id": 101, "name": "Quarto Duplo com Varanda"},
            {"id": 102, "name": "Quarto Triplo com Vista para a Piscina"},
            {"id": 103, "name": "Quarto Superior com Cama King-size 1"},
            {"id": 104, "name": "Quarto Superior com Cama King-size 2"},
        ],
    }


def test_match_room():
    assert seed.match_room("Quarto Duplo com Varanda") == "duplo-varanda"
    assert seed.match_room("Quarto Triplo com Vista para a Piscina") == "triplo-vista-piscina"
    assert seed.match_room("Quarto Superior com Cama King-size 1") == "superior-king-1"
    assert seed.match_room("Quarto Superior com Cama King-size 2") == "superior-king-2"
    assert seed.match_room("Sala de estar") is None


def test_seed_inserts_property_and_four_rooms(conn):
    with conn.cursor() as cur:
        out = seed.seed_property_and_rooms(cur, _payload())
        cur.execute("select count(*) from casa_angelina.rooms where property_id=%s",
                    (out["property_id"],))
        assert cur.fetchone()[0] == 4
        assert set(out["rooms_by_beds24_id"].keys()) == {"101", "102", "103", "104"}


def test_seed_is_idempotent(conn):
    with conn.cursor() as cur:
        a = seed.seed_property_and_rooms(cur, _payload())
        b = seed.seed_property_and_rooms(cur, _payload())
        assert a["property_id"] == b["property_id"]
        cur.execute("select count(*) from casa_angelina.rooms where property_id=%s",
                    (a["property_id"],))
        assert cur.fetchone()[0] == 4  # nao duplicou


def test_seed_raises_on_unknown_room(conn):
    payload = _payload()
    payload["roomTypes"].append({"id": 999, "name": "Quarto Fantasma"})
    with conn.cursor() as cur:
        with pytest.raises(ValueError):
            seed.seed_property_and_rooms(cur, payload)
```

- [ ] **Step 2: Rodar o teste (deve falhar)**

Run: `python -m pytest tools/beds24/test_seed.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'seed'`).

- [ ] **Step 3: Escrever `tools/beds24/seed.py`**

```python
CANONICAL_ROOMS = [
    {"slug": "duplo-varanda", "name": "Quarto Duplo com Varanda",
     "capacity": 2, "sort_order": 1, "match": "duplo"},
    {"slug": "triplo-vista-piscina", "name": "Quarto Triplo com Vista para a Piscina",
     "capacity": 3, "sort_order": 2, "match": "triplo"},
    {"slug": "superior-king-1", "name": "Quarto Superior com Cama King-size 1",
     "capacity": 2, "sort_order": 3, "match": "superior1"},
    {"slug": "superior-king-2", "name": "Quarto Superior com Cama King-size 2",
     "capacity": 2, "sort_order": 4, "match": "superior2"},
]
_BY_SLUG = {r["slug"]: r for r in CANONICAL_ROOMS}


def match_room(beds24_room_name):
    n = (beds24_room_name or "").strip().lower()
    if "duplo" in n:
        return "duplo-varanda"
    if "triplo" in n:
        return "triplo-vista-piscina"
    if "superior" in n and "1" in n:
        return "superior-king-1"
    if "superior" in n and "2" in n:
        return "superior-king-2"
    return None


def seed_property_and_rooms(cur, property_payload):
    beds24_property_id = str(property_payload["id"])
    name = property_payload.get("name") or "Casa Angelina"
    cur.execute(
        "insert into casa_angelina.properties (beds24_property_id,name,slug) "
        "values (%s,%s,'casa-angelina') "
        "on conflict (beds24_property_id) do update set name=excluded.name, updated_at=now() "
        "returning id",
        (beds24_property_id, name),
    )
    property_id = cur.fetchone()[0]

    rooms_by_beds24_id = {}
    room_types = property_payload.get("roomTypes") or []
    for rt in room_types:
        slug = match_room(rt.get("name"))
        if slug is None:
            raise ValueError(f"roomType do Beds24 nao casa com quarto canonico: {rt.get('name')!r}")
        spec = _BY_SLUG[slug]
        beds24_room_id = str(rt["id"])
        cur.execute(
            "insert into casa_angelina.rooms "
            "(property_id,beds24_room_id,name,slug,capacity,sort_order) "
            "values (%s,%s,%s,%s,%s,%s) "
            "on conflict (beds24_room_id) do update set "
            "name=excluded.name, capacity=excluded.capacity, sort_order=excluded.sort_order, "
            "updated_at=now() returning id",
            (property_id, beds24_room_id, spec["name"], spec["slug"],
             spec["capacity"], spec["sort_order"]),
        )
        rooms_by_beds24_id[beds24_room_id] = cur.fetchone()[0]
    return {"property_id": property_id, "rooms_by_beds24_id": rooms_by_beds24_id}
```

- [ ] **Step 4: Rodar os testes (devem passar)**

Run: `python -m pytest tools/beds24/test_seed.py -v`
Expected: PASS (4 passed). Nota: o upsert usa `on conflict` nas chaves únicas `beds24_property_id` e `beds24_room_id` (definidas no Plano 1).

- [ ] **Step 5: Commit**

```bash
git add tools/beds24/seed.py tools/beds24/test_seed.py
git commit -m "Painel 2a: seed data-driven da property + 4 quartos canonicos"
```

---

### Task 6: Orquestração do backfill (seed → paginação → upsert → cursor)

**Files:**
- Create: `tools/beds24/backfill.py`
- Test: `tools/beds24/test_backfill.py`

**Interfaces:**
- Consumes: `seed.*`, `upsert.*`, `mapping.*`, `client.Beds24Client`, fixture `conn`.
- Produces:
  - `run_backfill(conn, client) -> dict` — busca properties, faz seed, itera bookings, resolve+upsert cada um (reserva ou bloqueio conforme status), grava `sync_state`, retorna stats `{"reservations":n,"blocks":n,"skipped":n}`. Faz `conn.commit()` no fim.
  - Bloco `__main__` que abre conexão real e um `Beds24Client` com token de `auth.get_access_token()`.

- [ ] **Step 1: Escrever o teste `tools/beds24/test_backfill.py`** (client fake, DB real)

```python
import backfill


class FakeClient:
    def __init__(self, properties, bookings):
        self._properties = properties
        self._bookings = bookings

    def get_properties(self):
        return self._properties

    def get_bookings(self, **params):
        return self._bookings


def _properties():
    return [{
        "id": 4242, "name": "Casa Angelina",
        "roomTypes": [
            {"id": 101, "name": "Quarto Duplo com Varanda"},
            {"id": 102, "name": "Quarto Triplo com Vista para a Piscina"},
            {"id": 103, "name": "Quarto Superior com Cama King-size 1"},
            {"id": 104, "name": "Quarto Superior com Cama King-size 2"},
        ],
    }]


def _bookings():
    return [
        {"id": 1, "roomId": 101, "status": "Confirmed", "arrival": "2026-04-01",
         "departure": "2026-04-03", "numAdult": 2, "numChild": 0, "firstName": "A",
         "lastName": "A", "email": "a@x.com", "phone": "1", "country": "BR",
         "price": "800.00", "apiSourceId": 19, "masterId": 1,
         "modifiedTime": "2026-03-01 10:00:00"},
        {"id": 2, "roomId": 102, "status": "Black", "arrival": "2026-05-01",
         "departure": "2026-05-04", "modifiedTime": "2026-03-01 10:00:00"},
    ]


def test_run_backfill_creates_reservation_and_block(conn):
    client = FakeClient(_properties(), _bookings())
    stats = backfill.run_backfill(conn, client)
    assert stats["reservations"] == 1
    assert stats["blocks"] == 1
    with conn.cursor() as cur:
        cur.execute("select count(*) from casa_angelina.reservations where beds24_booking_id='1'")
        assert cur.fetchone()[0] == 1
        cur.execute("select count(*) from casa_angelina.calendar_blocks where source='beds24'")
        assert cur.fetchone()[0] >= 1
    # limpa (o teste comitou; nao deixar lixo no banco compartilhado)
    _cleanup(conn)


def test_run_backfill_is_idempotent(conn):
    client = FakeClient(_properties(), _bookings())
    backfill.run_backfill(conn, client)
    backfill.run_backfill(conn, client)
    with conn.cursor() as cur:
        cur.execute("select count(*) from casa_angelina.reservations where beds24_booking_id='1'")
        assert cur.fetchone()[0] == 1  # nao duplicou apos 2 rodadas
    _cleanup(conn)


def _cleanup(conn):
    with conn.cursor() as cur:
        cur.execute("delete from casa_angelina.properties where beds24_property_id='4242'")
    conn.commit()
```

- [ ] **Step 2: Rodar o teste (deve falhar)**

Run: `python -m pytest tools/beds24/test_backfill.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'backfill'`).

- [ ] **Step 3: Escrever `tools/beds24/backfill.py`**

```python
import json
import mapping
import seed as seed_mod
import upsert


def run_backfill(conn, client):
    stats = {"reservations": 0, "blocks": 0, "skipped": 0}
    with conn.cursor() as cur:
        properties = client.get_properties()
        if not properties:
            raise RuntimeError("Beds24 nao retornou nenhuma propriedade")
        seeded = seed_mod.seed_property_and_rooms(cur, properties[0])
        property_id = seeded["property_id"]
        rooms = seeded["rooms_by_beds24_id"]

        for b in client.get_bookings(propertyId=properties[0]["id"]):
            room_id = rooms.get(str(b.get("roomId")))
            if room_id is None:
                room_id = upsert.resolve_room_id(cur, property_id, b.get("roomId"))
            if room_id is None:
                stats["skipped"] += 1
                continue
            if mapping.is_block(b.get("status")):
                upsert.upsert_block(cur, property_id, room_id, b)
                stats["blocks"] += 1
            else:
                guest_id = upsert.resolve_or_create_guest(cur, property_id, b)
                upsert.upsert_reservation(cur, property_id, room_id, guest_id, b)
                stats["reservations"] += 1

        cur.execute(
            "insert into casa_angelina.sync_state (key,value,updated_at) "
            "values ('last_backfill', %s, now()) "
            "on conflict (key) do update set value=excluded.value, updated_at=now()",
            (json.dumps(stats),),
        )
    conn.commit()
    return stats


if __name__ == "__main__":
    from db import connect
    from client import Beds24Client
    from auth import get_access_token

    conn = connect()
    try:
        client = Beds24Client(get_access_token())
        print("backfill:", run_backfill(conn, client))
    finally:
        conn.close()
```

- [ ] **Step 4: Rodar os testes (devem passar)**

Run: `python -m pytest tools/beds24/test_backfill.py -v`
Expected: PASS (2 passed). Estes testes **comitam** no banco real e limpam via `_cleanup` no fim (usam a property de teste `4242`, isolada da real).

- [ ] **Step 5: Rodar a suíte inteira de `tools/beds24` (offline)**

Run: `python -m pytest tools/beds24 -v`
Expected: PASS (todos). Nenhuma chamada à API do Beds24 (só HTTP fake + banco real).

- [ ] **Step 6: Commit**

```bash
git add tools/beds24/backfill.py tools/beds24/test_backfill.py
git commit -m "Painel 2a: orquestracao do backfill (seed + upsert + cursor em sync_state)"
```

---

### Task 7: Execução ao vivo — probe, seed e backfill reais (NECESSITA TOKEN DO BEDS24)

> **Checkpoint de token.** Esta task usa a API real do Beds24. O controlador (subagent-driven-development) deve, ANTES de despachar esta task, pedir ao dono o **invite code** do Beds24 e recebê-lo aqui. Instruções para o dono gerar o code: painel Beds24 → **Account → Account Access / API** (`control3.php?pagetype=apiv2`) → gerar **invite code** com escopos de leitura `read:bookings`, `read:properties`, `read:inventory` → copiar o code (validade curta) e enviar. O controlador grava o refresh token via `auth.bootstrap_from_invite(code)` (que escreve em `.beds24auth`). Não commitar `.beds24auth`.

**Files:**
- Create: `tools/beds24/probe.py` (dump do JSON cru para confirmar campos)
- Create: `tools/beds24/fixtures/` (JSON cru capturado — gitignored se contiver dado de hóspede real)
- Modify: `.gitignore` (adicionar `tools/beds24/fixtures/`)

**Interfaces:**
- Consumes: `auth`, `client`, `backfill`, `.beds24auth` (refresh token já gravado pelo controlador).

- [ ] **Step 1: Confirmar que o refresh token existe**

Run: `python -c "import sys; sys.path.insert(0,'tools/beds24'); from auth import load_beds24_env; print('BEDS24_REFRESH_TOKEN' in load_beds24_env('.beds24auth'))"`
Expected: `True`. Se `False`, PARAR e reportar NEEDS_CONTEXT (o controlador precisa rodar `bootstrap_from_invite` com o invite code do dono).

- [ ] **Step 2: Escrever `tools/beds24/probe.py`**

```python
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_access_token
from client import Beds24Client

OUT = os.path.join(os.path.dirname(__file__), "fixtures")


def main():
    os.makedirs(OUT, exist_ok=True)
    client = Beds24Client(get_access_token())
    props = client.get_properties()
    with open(os.path.join(OUT, "properties.json"), "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)
    bookings = client.get_bookings()
    with open(os.path.join(OUT, "bookings.json"), "w", encoding="utf-8") as f:
        json.dump(bookings[:10], f, ensure_ascii=False, indent=2)
    print(f"properties: {len(props)}; bookings capturados: {len(bookings)}")
    if props:
        print("roomTypes:", [rt.get("name") for rt in (props[0].get("roomTypes") or [])])
    if bookings:
        print("campos do 1o booking:", sorted(bookings[0].keys()))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Adicionar `tools/beds24/fixtures/` ao `.gitignore`** (o JSON cru contém dado de hóspede — LGPD)

Acrescentar `tools/beds24/fixtures/` ao `.gitignore`.

- [ ] **Step 4: Rodar o probe e conferir os campos reais**

Run: `python tools/beds24/probe.py`
Expected: imprime a contagem de properties/bookings, os nomes dos roomTypes e as chaves do primeiro booking. **Verificar manualmente** que os campos usados no `mapping.py` existem no payload real: `id`, `roomId`, `status`, `arrival`, `departure`, `numAdult`, `numChild`, `firstName`/`lastName`, `email`, `phone`, `country`, `price`, `apiSourceId`, `masterId`, `modifiedTime`. Que os nomes dos roomTypes casem com `seed.match_room`. E que os valores de `apiSourceId` batam com o mapa (0/19/46).

- [ ] **Step 5: Se algum campo divergir, ajustar `mapping.py`/`seed.py` e re-rodar os testes offline**

Se o probe mostrar nome de campo diferente (ex.: `numadult` minúsculo, `checkIn` em vez de `arrival`, `sourceId` em vez de `apiSourceId`), ajustar o acesso no `mapping.py` (e as fixtures dos testes se necessário) e rodar `python -m pytest tools/beds24 -v` até verde. Reportar como DONE_WITH_CONCERNS listando cada divergência corrigida. Se nada divergir, seguir.

- [ ] **Step 6: Rodar o backfill real**

Run: `python tools/beds24/backfill.py`
Expected: `backfill: {'reservations': N, 'blocks': M, 'skipped': 0}` com N ≥ 0 coerente com o volume de reservas no Beds24. `skipped` deve ser 0 (todo `roomId` resolve; se não, investigar o mapeamento de quartos).

- [ ] **Step 7: Provar idempotência ao vivo (rodar de novo, contar antes e depois)**

Run:
```bash
python -c "import sys; sys.path.insert(0,'tools/beds24'); from db import connect; c=connect(); cur=c.cursor(); cur.execute('select count(*) from casa_angelina.reservations'); print('antes:', cur.fetchone()[0]); c.close()"
python tools/beds24/backfill.py
python -c "import sys; sys.path.insert(0,'tools/beds24'); from db import connect; c=connect(); cur=c.cursor(); cur.execute('select count(*) from casa_angelina.reservations'); print('depois:', cur.fetchone()[0]); c.close()"
```
Expected: `antes` == `depois` (segunda rodada não cria linha nova). Prova a idempotência com dados reais.

- [ ] **Step 8: Commit**

```bash
git add tools/beds24/probe.py .gitignore
git commit -m "Painel 2a: probe + backfill real do Beds24 (idempotencia provada ao vivo)"
```

> `.beds24auth` e `tools/beds24/fixtures/` NÃO entram no commit (gitignored). Conferir com `git status` antes de commitar.

---

## Self-Review

- **Cobertura do design:** auth (§3) → Task 1; client/backfill flow (§4) → Tasks 2, 6, 7; mapa de dados (§5) → Task 3; seed data-driven (§6) → Task 5; idempotência (§7) → Tasks 4, 6, 7; testes (§8) → todas; itens em aberto/probe (§10) → Task 7. Sem lacunas dentro do recorte 2a.
- **Sem placeholders:** todo código e todos os testes estão completos e executáveis. A única incerteza real (nomes de campo da API) é tratada por um passo de probe explícito (Task 7, Steps 4-5) que valida e corrige contra o payload real, com re-teste — não é um placeholder, é um gate.
- **Consistência de tipos/nomes:** `map_status/map_channel/map_booking_to_reservation/map_booking_to_block/guest_fields/is_block` (Task 3) são consumidos com as mesmas assinaturas em `upsert.py` (Task 4) e `backfill.py` (Task 6). `seed_property_and_rooms` retorna `{"property_id","rooms_by_beds24_id"}`, consumido igual no backfill. `db.connect()` (Task 4) reusado por conftest e pelo `__main__` do backfill (Task 6) e pelo probe (Task 7). `Beds24Client.get_properties/get_bookings` (Task 2) batem com o `FakeClient` do teste e com o uso real.
- **Isolamento do banco compartilhado:** testes de mapping/auth/client não tocam o banco; testes de upsert/seed usam a fixture `conn` (rollback); os testes de backfill comitam mas limpam via `_cleanup` usando a property de teste `4242`, isolada da real.
