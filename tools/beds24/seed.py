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

# Mapeamento autoritativo beds24_room_id -> slug canonico (especifico deste deployment).
# Necessario porque o Beds24 TRUNCA nomes de quarto em 50 chars: com o prefixo
# "Casa Angelina (Pousada), " que veio do Airbnb, os dois Superior King ficam com nome
# truncado IDENTICO e nao dao pra distinguir por nome. Mapear por id resolve.
# (Quando o painel virar template p/ outros clientes, isto sai para config por-cliente.)
CASA_ANGELINA_ROOM_MAP = {
    "710280": "duplo-varanda",
    "710281": "triplo-vista-piscina",
    "710282": "superior-king-1",
    "710283": "superior-king-2",
}


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


def seed_property_and_rooms(cur, property_payload, room_map=None):
    if room_map is None:
        room_map = CASA_ANGELINA_ROOM_MAP
    beds24_property_id = str(property_payload["id"])
    name = property_payload.get("name") or "Casa Angelina"
    slug = "prop-" + beds24_property_id
    cur.execute(
        "insert into casa_angelina.properties (beds24_property_id,name,slug) "
        "values (%s,%s,%s) "
        "on conflict (beds24_property_id) do update set name=excluded.name, updated_at=now() "
        "returning id",
        (beds24_property_id, name, slug),
    )
    property_id = cur.fetchone()[0]

    rooms_by_beds24_id = {}
    seeded_slugs = set()
    for rt in property_payload.get("roomTypes") or []:
        beds24_room_id = str(rt["id"])
        slug = room_map.get(beds24_room_id) or match_room(rt.get("name"))
        if slug is None:
            continue  # quarto nao reconhecido (ex.: placeholder "Room 1" do Beds24) -> ignora
        spec = _BY_SLUG[slug]
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
        seeded_slugs.add(slug)

    missing = [s for s in _BY_SLUG if s not in seeded_slugs]
    if missing:
        raise ValueError(f"quartos canonicos ausentes no payload do Beds24: {missing}")
    return {"property_id": property_id, "rooms_by_beds24_id": rooms_by_beds24_id}
