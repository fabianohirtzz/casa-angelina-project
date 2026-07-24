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
