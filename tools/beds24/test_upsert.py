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
