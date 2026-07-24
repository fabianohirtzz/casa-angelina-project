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
