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
