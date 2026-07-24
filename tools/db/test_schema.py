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
