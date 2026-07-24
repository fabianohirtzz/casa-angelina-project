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
