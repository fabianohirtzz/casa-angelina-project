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


def test_seed_ignores_unmapped_extra_room(conn):
    payload = _payload()
    payload["roomTypes"].insert(0, {"id": 710279, "name": "Room 1"})  # placeholder do Beds24
    with conn.cursor() as cur:
        out = seed.seed_property_and_rooms(cur, payload)
        cur.execute("select count(*) from casa_angelina.rooms where property_id=%s",
                    (out["property_id"],))
        assert cur.fetchone()[0] == 4  # Room 1 ignorado, 4 canonicos seedados
        assert "710279" not in out["rooms_by_beds24_id"]


def test_seed_raises_when_canonical_missing(conn):
    payload = _payload()
    payload["roomTypes"] = payload["roomTypes"][:3]  # remove um quarto canonico
    with conn.cursor() as cur:
        with pytest.raises(ValueError):
            seed.seed_property_and_rooms(cur, payload)


def test_seed_maps_superiors_by_id_when_names_truncated(conn):
    # reproduz a realidade: Beds24 trunca nomes em 50 chars, deixando os 2 Superior
    # identicos por nome. ids sinteticos + room_map explicito -> isolado de dados reais.
    trunc = "Casa Angelina (Pousada), Quarto Superior com Ca..."
    payload = {
        "id": 4242, "name": "Casa Angelina",
        "roomTypes": [
            {"id": 101, "name": "Casa Angelina (Pousada), Quarto Duplo com Varanda"},
            {"id": 102, "name": "Casa Angelina (Pousada), Quarto Triplo com Vist..."},
            {"id": 103, "name": trunc},
            {"id": 104, "name": trunc},
        ],
    }
    room_map = {"103": "superior-king-1", "104": "superior-king-2"}
    with conn.cursor() as cur:
        out = seed.seed_property_and_rooms(cur, payload, room_map=room_map)
        rid_1 = out["rooms_by_beds24_id"]["103"]
        rid_2 = out["rooms_by_beds24_id"]["104"]
        cur.execute("select slug from casa_angelina.rooms where id=%s", (rid_1,))
        assert cur.fetchone()[0] == "superior-king-1"
        cur.execute("select slug from casa_angelina.rooms where id=%s", (rid_2,))
        assert cur.fetchone()[0] == "superior-king-2"
