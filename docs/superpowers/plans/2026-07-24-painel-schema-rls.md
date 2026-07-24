# Painel — Plano 1: Schema `casa_angelina` + RLS (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o schema `casa_angelina` (8 tabelas) no Supabase compartilhado do HD360, com RLS gated por membro, provado por testes.

**Architecture:** Migrações SQL idempotentes aplicadas ao Postgres remoto (schema isolado `casa_angelina`, sem tocar em `public`). Um harness Python (psycopg2) aplica as migrações e roda os testes contra o banco remoto, simulando os roles `anon`/`authenticated` para provar o RLS. Sem Supabase CLI/Docker nesta fatia.

**Tech Stack:** PostgreSQL 17 (Supabase), SQL, Python 3 + psycopg2-binary + pytest.

**Escopo:** Este é o **Plano 1 de 2** da fatia 1. Entrega schema + RLS testados. O **Plano 2** (espelhamento Beds24 via Edge Functions + seed com ids reais do Beds24) vem depois, quando houver `service_role` key + token da API v2 do Beds24. Base: `docs/superpowers/specs/2026-07-24-painel-fundacao-dados-beds24-sync-design.md`.

## Global Constraints

- **Schema alvo:** `casa_angelina`. NUNCA criar/alterar objetos em `public` (é do HD360).
- **RLS obrigatório** em todas as tabelas `casa_angelina.*` (dado de hóspede é LGPD; anon key é pública).
- **Isolamento de tenant:** Auth é compartilhado com o HD360 → acesso gated por `casa_angelina.app_users` via `casa_angelina.is_member()`. `anon` = zero acesso.
- **Migrações idempotentes** (re-executáveis): `create ... if not exists`, `drop policy if exists` antes de `create policy`, `create or replace function`.
- **Segredos** (`SUPABASE_DB_URL` etc.) só em `.supabaseauth` (gitignored). Nunca no git nem em código commitado.
- **Conexão ao banco:** direta é IPv6-only; a senha tem `@` → já vem URL-encoded como `%40` em `SUPABASE_DB_URL`.

## File Structure

- `tools/db/apply.py` — aplica um arquivo `.sql` ao banco remoto (lê `.supabaseauth`).
- `tools/db/conftest.py` — fixture pytest de conexão (transação + rollback).
- `tools/db/test_schema.py` — testes de existência de tabelas e constraints.
- `tools/db/test_rls.py` — testes de RLS (anon negado, membro permitido, não-membro negado).
- `tools/db/requirements.txt` — `psycopg2-binary`, `pytest`.
- `supabase/migrations/0001_casa_angelina_schema.sql` — schema + 8 tabelas + constraints + índices.
- `supabase/migrations/0002_casa_angelina_rls.sql` — `is_member()` + enable RLS + policies + grants.

---

### Task 1: Harness de banco (aplicar migrações + rodar testes)

**Files:**
- Create: `tools/db/apply.py`
- Create: `tools/db/conftest.py`
- Create: `tools/db/requirements.txt`
- Test: `tools/db/test_connection.py`

**Interfaces:**
- Consumes: `.supabaseauth` (chave `SUPABASE_DB_URL`).
- Produces: `tools/db/apply.py` CLI (`python tools/db/apply.py <arquivo.sql>`); fixture pytest `conn` (psycopg2 connection, rollback no teardown) via `conftest.py`.

- [ ] **Step 1: Criar `tools/db/requirements.txt`**

```
psycopg2-binary
pytest
```

- [ ] **Step 2: Criar o helper de conexão + apply em `tools/db/apply.py`**

```python
import sys
import psycopg2


def load_env(path=".supabaseauth"):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k] = v
    return env


def db_url():
    url = load_env()["SUPABASE_DB_URL"]
    return url + ("&" if "?" in url else "?") + "sslmode=require"


def apply_file(path):
    sql = open(path, encoding="utf-8").read()
    conn = psycopg2.connect(db_url(), connect_timeout=20)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.close()
    print("aplicado:", path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python tools/db/apply.py <arquivo.sql>")
        sys.exit(2)
    apply_file(sys.argv[1])
```

- [ ] **Step 3: Criar a fixture pytest em `tools/db/conftest.py`**

```python
import pytest
from apply import db_url
import psycopg2


@pytest.fixture
def conn():
    c = psycopg2.connect(db_url(), connect_timeout=20)
    try:
        yield c
    finally:
        c.rollback()
        c.close()
```

- [ ] **Step 4: Escrever o teste de conexão `tools/db/test_connection.py`**

```python
def test_can_connect_and_query(conn):
    with conn.cursor() as cur:
        cur.execute("select 1")
        assert cur.fetchone()[0] == 1
```

- [ ] **Step 5: Instalar deps e rodar o teste**

Run: `python -m pip install -q -r tools/db/requirements.txt && python -m pytest tools/db/test_connection.py -v`
Expected: PASS (1 passed). A conexão usa `.supabaseauth`.

- [ ] **Step 6: Commit**

```bash
git add tools/db/apply.py tools/db/conftest.py tools/db/requirements.txt tools/db/test_connection.py
git commit -m "Painel: harness de banco (apply + fixture pytest)"
```

---

### Task 2: Migração do schema (8 tabelas)

**Files:**
- Create: `supabase/migrations/0001_casa_angelina_schema.sql`
- Test: `tools/db/test_schema.py`

**Interfaces:**
- Consumes: `tools/db/apply.py`, fixture `conn`.
- Produces: schema `casa_angelina` com tabelas `properties, rooms, guests, reservations, calendar_blocks, app_users, beds24_webhook_events, sync_state`. Chaves usadas por tarefas/planos seguintes: `properties(id, beds24_property_id)`, `rooms(id, property_id, beds24_room_id)`, `reservations` com `unique(beds24_booking_id, room_id)` e `check(check_out > check_in)`, `app_users(user_id, property_id, role)`.

- [ ] **Step 1: Escrever a migração `supabase/migrations/0001_casa_angelina_schema.sql`**

```sql
create schema if not exists casa_angelina;

create table if not exists casa_angelina.properties (
  id uuid primary key default gen_random_uuid(),
  beds24_property_id text unique not null,
  name text not null,
  slug text unique not null,
  timezone text not null default 'America/Bahia',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists casa_angelina.rooms (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  beds24_room_id text unique not null,
  name text not null,
  slug text not null,
  capacity int not null check (capacity > 0),
  sort_order int not null default 0,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (property_id, slug)
);

create table if not exists casa_angelina.guests (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  full_name text,
  email text,
  phone text,
  country text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists guests_property_email_idx on casa_angelina.guests (property_id, email);
create index if not exists guests_property_phone_idx on casa_angelina.guests (property_id, phone);

create table if not exists casa_angelina.reservations (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  room_id uuid not null references casa_angelina.rooms(id),
  guest_id uuid references casa_angelina.guests(id),
  beds24_booking_id text,
  group_ref text,
  channel text not null check (channel in ('booking','airbnb','direct','manual')),
  status text not null check (status in ('confirmed','pending','cancelled','no_show')),
  check_in date not null,
  check_out date not null,
  num_guests int check (num_guests is null or num_guests > 0),
  total_amount numeric(12,2),
  currency text not null default 'BRL',
  raw_payload jsonb,
  beds24_modified_at timestamptz,
  synced_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (check_out > check_in),
  unique (beds24_booking_id, room_id)
);
create index if not exists reservations_property_dates_idx on casa_angelina.reservations (property_id, check_in, check_out);
create index if not exists reservations_room_dates_idx on casa_angelina.reservations (room_id, check_in, check_out);
create index if not exists reservations_group_ref_idx on casa_angelina.reservations (group_ref);

create table if not exists casa_angelina.calendar_blocks (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  room_id uuid not null references casa_angelina.rooms(id),
  start_date date not null,
  end_date date not null,
  reason text,
  source text not null check (source in ('beds24','manual')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (end_date > start_date)
);

create table if not exists casa_angelina.app_users (
  user_id uuid primary key references auth.users(id) on delete cascade,
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  role text not null check (role in ('admin','operador')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists casa_angelina.beds24_webhook_events (
  id bigint generated always as identity primary key,
  event_type text,
  beds24_booking_id text,
  payload jsonb,
  received_at timestamptz not null default now(),
  processed_at timestamptz,
  status text not null default 'received' check (status in ('received','processed','error')),
  error text
);

create table if not exists casa_angelina.sync_state (
  key text primary key,
  value jsonb,
  updated_at timestamptz not null default now()
);
```

- [ ] **Step 2: Aplicar a migração**

Run: `python tools/db/apply.py supabase/migrations/0001_casa_angelina_schema.sql`
Expected: `aplicado: supabase/migrations/0001_casa_angelina_schema.sql`

- [ ] **Step 3: Escrever os testes de schema em `tools/db/test_schema.py`**

```python
import psycopg2
import pytest

TABLES = [
    "properties", "rooms", "guests", "reservations",
    "calendar_blocks", "app_users", "beds24_webhook_events", "sync_state",
]


def test_all_tables_exist(conn):
    with conn.cursor() as cur:
        cur.execute(
            "select table_name from information_schema.tables where table_schema='casa_angelina'"
        )
        found = {r[0] for r in cur.fetchall()}
    for t in TABLES:
        assert t in found, f"faltou tabela {t}"


def _seed_property_room(cur):
    cur.execute(
        "insert into casa_angelina.properties (beds24_property_id,name,slug) "
        "values ('t-prop','T','t-slug') returning id"
    )
    pid = cur.fetchone()[0]
    cur.execute(
        "insert into casa_angelina.rooms (property_id,beds24_room_id,name,slug,capacity) "
        "values (%s,'t-room','R','r',2) returning id",
        (pid,),
    )
    rid = cur.fetchone()[0]
    return pid, rid


def test_reservation_checkout_must_be_after_checkin(conn):
    with conn.cursor() as cur:
        pid, rid = _seed_property_room(cur)
        cur.execute("savepoint sp")
        with pytest.raises(psycopg2.errors.CheckViolation):
            cur.execute(
                "insert into casa_angelina.reservations "
                "(property_id,room_id,channel,status,check_in,check_out) "
                "values (%s,%s,'direct','confirmed','2026-01-05','2026-01-05')",
                (pid, rid),
            )
        cur.execute("rollback to savepoint sp")


def test_reservation_channel_check(conn):
    with conn.cursor() as cur:
        pid, rid = _seed_property_room(cur)
        cur.execute("savepoint sp")
        with pytest.raises(psycopg2.errors.CheckViolation):
            cur.execute(
                "insert into casa_angelina.reservations "
                "(property_id,room_id,channel,status,check_in,check_out) "
                "values (%s,%s,'tripadvisor','confirmed','2026-01-05','2026-01-06')",
                (pid, rid),
            )
        cur.execute("rollback to savepoint sp")


def test_reservation_unique_booking_room(conn):
    with conn.cursor() as cur:
        pid, rid = _seed_property_room(cur)
        cur.execute(
            "insert into casa_angelina.reservations "
            "(property_id,room_id,beds24_booking_id,channel,status,check_in,check_out) "
            "values (%s,%s,'B1','booking','confirmed','2026-01-05','2026-01-06')",
            (pid, rid),
        )
        cur.execute("savepoint sp")
        with pytest.raises(psycopg2.errors.UniqueViolation):
            cur.execute(
                "insert into casa_angelina.reservations "
                "(property_id,room_id,beds24_booking_id,channel,status,check_in,check_out) "
                "values (%s,%s,'B1','booking','confirmed','2026-02-05','2026-02-06')",
                (pid, rid),
            )
        cur.execute("rollback to savepoint sp")
```

- [ ] **Step 4: Rodar os testes**

Run: `python -m pytest tools/db/test_schema.py -v`
Expected: PASS (4 passed). Nenhuma linha persiste (fixture faz rollback).

- [ ] **Step 5: Commit**

```bash
git add supabase/migrations/0001_casa_angelina_schema.sql tools/db/test_schema.py
git commit -m "Painel: migracao do schema casa_angelina (8 tabelas)"
```

---

### Task 3: RLS — isolamento por membro (o portão de segurança)

**Files:**
- Create: `supabase/migrations/0002_casa_angelina_rls.sql`
- Test: `tools/db/test_rls.py`

**Interfaces:**
- Consumes: schema da Task 2; fixture `conn`.
- Produces: função `casa_angelina.is_member(uuid) returns boolean`; RLS ligado; policies de SELECT para `authenticated` membro; grants para `authenticated`. Garantia: `anon` e `authenticated` não-membro não leem nada.

- [ ] **Step 1: Escrever a migração `supabase/migrations/0002_casa_angelina_rls.sql`**

```sql
create or replace function casa_angelina.is_member(p_property_id uuid)
returns boolean
language sql
stable
security definer
set search_path = casa_angelina, public
as $$
  select exists (
    select 1 from casa_angelina.app_users au
    where au.user_id = auth.uid()
      and au.property_id = p_property_id
  );
$$;

alter table casa_angelina.properties          enable row level security;
alter table casa_angelina.rooms               enable row level security;
alter table casa_angelina.guests              enable row level security;
alter table casa_angelina.reservations        enable row level security;
alter table casa_angelina.calendar_blocks     enable row level security;
alter table casa_angelina.app_users           enable row level security;
alter table casa_angelina.beds24_webhook_events enable row level security;
alter table casa_angelina.sync_state          enable row level security;

drop policy if exists properties_select_member on casa_angelina.properties;
create policy properties_select_member on casa_angelina.properties
  for select to authenticated using (casa_angelina.is_member(id));

drop policy if exists rooms_select_member on casa_angelina.rooms;
create policy rooms_select_member on casa_angelina.rooms
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists guests_select_member on casa_angelina.guests;
create policy guests_select_member on casa_angelina.guests
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists reservations_select_member on casa_angelina.reservations;
create policy reservations_select_member on casa_angelina.reservations
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists calendar_blocks_select_member on casa_angelina.calendar_blocks;
create policy calendar_blocks_select_member on casa_angelina.calendar_blocks
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists app_users_select_self on casa_angelina.app_users;
create policy app_users_select_self on casa_angelina.app_users
  for select to authenticated using (user_id = auth.uid());

-- beds24_webhook_events e sync_state: sem policy => nenhum acesso de anon/authenticated.

grant usage on schema casa_angelina to authenticated;
grant select on
  casa_angelina.properties,
  casa_angelina.rooms,
  casa_angelina.guests,
  casa_angelina.reservations,
  casa_angelina.calendar_blocks,
  casa_angelina.app_users
  to authenticated;
```

- [ ] **Step 2: Aplicar a migração**

Run: `python tools/db/apply.py supabase/migrations/0002_casa_angelina_rls.sql`
Expected: `aplicado: supabase/migrations/0002_casa_angelina_rls.sql`

- [ ] **Step 3: Escrever os testes de RLS em `tools/db/test_rls.py`**

O harness conecta como `postgres` (superuser). Para provar o RLS, cada teste cria dados, depois usa `set local role` + `set local request.jwt.claims` para simular o que o PostgREST faz, e verifica o que cada papel enxerga. Tudo em savepoints, revertido no fim.

```python
import json
import psycopg2
import pytest


def _seed(cur):
    # cria um usuario auth, uma propriedade, um quarto e uma reserva
    cur.execute("insert into auth.users (id, email) values (gen_random_uuid(), 't@t.com') returning id")
    uid = cur.fetchone()[0]
    cur.execute(
        "insert into casa_angelina.properties (beds24_property_id,name,slug) "
        "values ('rls-prop','RLS','rls-slug') returning id"
    )
    pid = cur.fetchone()[0]
    cur.execute(
        "insert into casa_angelina.rooms (property_id,beds24_room_id,name,slug,capacity) "
        "values (%s,'rls-room','R','r',2) returning id",
        (pid,),
    )
    rid = cur.fetchone()[0]
    cur.execute(
        "insert into casa_angelina.reservations "
        "(property_id,room_id,channel,status,check_in,check_out) "
        "values (%s,%s,'booking','confirmed','2026-01-05','2026-01-06')",
        (pid, rid),
    )
    return uid, pid, rid


def _as_role(cur, role, uid=None):
    # define os claims do JWT ANTES de trocar de role (evita restricao de privilegio),
    # depois assume o role (RLS passa a valer). role e valor controlado (anon/authenticated).
    claims = json.dumps({"sub": str(uid), "role": role}) if uid else json.dumps({"role": role})
    cur.execute("select set_config('request.jwt.claims', %s, true)", (claims,))
    cur.execute("set local role " + role)


def _count_reservations(cur):
    cur.execute("select count(*) from casa_angelina.reservations")
    return cur.fetchone()[0]


def test_anon_cannot_access_schema(conn):
    # anon nao recebe usage no schema casa_angelina => acesso negado (garantia mais forte que 0 linhas)
    with conn.cursor() as cur:
        _seed(cur)
        cur.execute("savepoint sp")
        _as_role(cur, "anon")
        with pytest.raises(psycopg2.errors.InsufficientPrivilege):
            _count_reservations(cur)
        # apos erro a transacao fica abortada; rollback ao savepoint reverte dados E o set local role
        cur.execute("rollback to savepoint sp")


def test_member_sees_reservations(conn):
    with conn.cursor() as cur:
        uid, pid, rid = _seed(cur)
        cur.execute(
            "insert into casa_angelina.app_users (user_id,property_id,role) values (%s,%s,'admin')",
            (uid, pid),
        )
        cur.execute("savepoint sp")
        _as_role(cur, "authenticated", uid)
        assert _count_reservations(cur) >= 1
        cur.execute("rollback to savepoint sp")  # reverte dados e o role


def test_authenticated_non_member_sees_nothing(conn):
    with conn.cursor() as cur:
        uid, pid, rid = _seed(cur)
        # cria um SEGUNDO usuario que NAO e membro (simula usuario do HD360)
        cur.execute("insert into auth.users (id, email) values (gen_random_uuid(), 'hd360@t.com') returning id")
        other = cur.fetchone()[0]
        cur.execute("savepoint sp")
        _as_role(cur, "authenticated", other)
        assert _count_reservations(cur) == 0
        cur.execute("rollback to savepoint sp")  # reverte dados e o role
```

- [ ] **Step 4: Rodar os testes de RLS**

Run: `python -m pytest tools/db/test_rls.py -v`
Expected: PASS (3 passed). Prova: anon = 0, membro >= 1, authenticated não-membro = 0. Nada persiste.

- [ ] **Step 5: Rodar a suíte inteira (garante que schema + RLS convivem)**

Run: `python -m pytest tools/db -v`
Expected: PASS (todos). 

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/0002_casa_angelina_rls.sql tools/db/test_rls.py
git commit -m "Painel: RLS gated por membro no schema casa_angelina + testes"
```

---

## Passo manual (fora do código, após as migrações)

No dashboard do Supabase (projeto do HD360): **Settings → API → Exposed schemas** → adicionar
`casa_angelina`. Sem isso, a API REST/JS (anon/authenticated) não enxerga o schema — o RLS já está
pronto para quando isso for ligado. (Não afeta os testes deste plano, que vão direto no Postgres.)

## Depois deste plano

**Plano 2 (fatia 1, parte B):** espelhamento Beds24 → Supabase em Edge Functions (backfill,
webhook, reconcile) + seed da propriedade Casa Angelina e dos 4 quartos com os `beds24_*_id` reais.
Pré-requisitos que faltam: `service_role` key do Supabase, invite code/refresh token da API v2 do
Beds24, e setup de deploy de Edge Functions (Supabase CLI).

## Self-Review

- **Cobertura do spec:** schema (§3) → Tasks 2; RLS/isolamento (§5) → Task 3; harness/testes (§6) →
  Tasks 1-3. Sync (§4) e seed → deslocados para o Plano 2 (dependem de credenciais ausentes),
  registrado acima. Sem lacunas dentro do recorte deste plano.
- **Sem placeholders:** todo SQL e todos os testes estão completos e executáveis.
- **Consistência de tipos:** `is_member(uuid)` usado nas policies bate com a definição; nomes de
  tabelas/colunas idênticos entre migração e testes; `unique(beds24_booking_id, room_id)` testado.
