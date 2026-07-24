import json
import mapping


def resolve_room_id(cur, property_id, beds24_room_id):
    cur.execute(
        "select id from casa_angelina.rooms where property_id=%s and beds24_room_id=%s",
        (property_id, str(beds24_room_id)),
    )
    row = cur.fetchone()
    return row[0] if row else None


def resolve_or_create_guest(cur, property_id, booking):
    g = mapping.guest_fields(booking)
    if g["email"]:
        cur.execute(
            "select id from casa_angelina.guests where property_id=%s and email=%s",
            (property_id, g["email"]),
        )
        row = cur.fetchone()
        if row:
            return row[0]
    if g["phone"]:
        cur.execute(
            "select id from casa_angelina.guests where property_id=%s and phone=%s",
            (property_id, g["phone"]),
        )
        row = cur.fetchone()
        if row:
            return row[0]
    if not any([g["full_name"], g["email"], g["phone"]]):
        return None
    cur.execute(
        "insert into casa_angelina.guests (property_id,full_name,email,phone,country) "
        "values (%s,%s,%s,%s,%s) returning id",
        (property_id, g["full_name"], g["email"], g["phone"], g["country"]),
    )
    return cur.fetchone()[0]


def upsert_reservation(cur, property_id, room_id, guest_id, booking):
    row = mapping.map_booking_to_reservation(booking, room_id, guest_id)
    cur.execute(
        "select id, beds24_modified_at from casa_angelina.reservations "
        "where beds24_booking_id=%s and room_id=%s",
        (row["beds24_booking_id"], room_id),
    )
    existing = cur.fetchone()
    payload = json.dumps(row["raw_payload"])
    if existing:
        res_id = existing[0]
        new_mod = row["beds24_modified_at"]
        # guarda de idempotencia FEITA EM SQL (compara timestamptz, nao string):
        # so atualiza se o gravado for null ou mais antigo que o modifiedTime do payload.
        cur.execute(
            "update casa_angelina.reservations set "
            "guest_id=%s, group_ref=%s, channel=%s, status=%s, check_in=%s, check_out=%s, "
            "num_guests=%s, total_amount=%s, beds24_modified_at=%s, raw_payload=%s, "
            "synced_at=now(), updated_at=now() "
            "where id=%s and (beds24_modified_at is null or beds24_modified_at < %s::timestamptz)",
            (guest_id, row["group_ref"], row["channel"], row["status"], row["check_in"],
             row["check_out"], row["num_guests"], row["total_amount"],
             row["beds24_modified_at"], payload, res_id, new_mod),
        )
        return res_id
    cur.execute(
        "insert into casa_angelina.reservations "
        "(property_id,room_id,guest_id,beds24_booking_id,group_ref,channel,status,"
        "check_in,check_out,num_guests,total_amount,raw_payload,beds24_modified_at,synced_at) "
        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now()) returning id",
        (property_id, room_id, guest_id, row["beds24_booking_id"], row["group_ref"],
         row["channel"], row["status"], row["check_in"], row["check_out"],
         row["num_guests"], row["total_amount"], payload, row["beds24_modified_at"]),
    )
    return cur.fetchone()[0]


def upsert_block(cur, property_id, room_id, booking):
    blk = mapping.map_booking_to_block(booking, room_id)
    cur.execute(
        "select id from casa_angelina.calendar_blocks "
        "where room_id=%s and start_date=%s and end_date=%s and source='beds24'",
        (room_id, blk["start_date"], blk["end_date"]),
    )
    if cur.fetchone():
        return
    cur.execute(
        "insert into casa_angelina.calendar_blocks "
        "(property_id,room_id,start_date,end_date,reason,source) "
        "values (%s,%s,%s,%s,%s,'beds24')",
        (property_id, room_id, blk["start_date"], blk["end_date"], blk["reason"]),
    )
