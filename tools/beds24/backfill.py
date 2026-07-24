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
