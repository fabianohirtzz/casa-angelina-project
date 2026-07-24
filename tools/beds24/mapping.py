_STATUS = {
    "new": "confirmed",
    "confirmed": "confirmed",
    "request": "pending",
    "inquiry": "pending",
    "cancelled": "cancelled",
    "canceled": "cancelled",
}

_CHANNEL = {0: "direct", 19: "booking", 46: "airbnb"}


def _norm(status):
    return (status or "").strip().lower()


def is_block(beds24_status):
    return _norm(beds24_status) == "black"


def map_status(beds24_status):
    if is_block(beds24_status):
        return None
    s = _norm(beds24_status)
    if s not in _STATUS:
        raise ValueError(f"status Beds24 desconhecido: {beds24_status!r}")
    return _STATUS[s]


def map_channel(api_source_id):
    try:
        return _CHANNEL.get(int(api_source_id), "manual")
    except (TypeError, ValueError):
        return "manual"


def guest_fields(b):
    name = " ".join(x for x in [b.get("firstName"), b.get("lastName")] if x).strip()
    return {
        "full_name": name or None,
        "email": b.get("email"),
        "phone": b.get("phone") or b.get("mobile"),
        "country": b.get("country"),
    }


def _num_guests(b):
    total = (b.get("numAdult") or 0) + (b.get("numChild") or 0)
    return total or None


def map_booking_to_reservation(b, room_id, guest_id):
    return {
        "room_id": room_id,
        "guest_id": guest_id,
        "beds24_booking_id": str(b["id"]),
        "group_ref": str(b["masterId"]) if b.get("masterId") else None,
        "channel": map_channel(b.get("apiSourceId")),
        "status": map_status(b.get("status")),
        "check_in": b["arrival"],
        "check_out": b["departure"],
        "num_guests": _num_guests(b),
        "total_amount": b.get("price"),
        "beds24_modified_at": b.get("modifiedTime"),
        "raw_payload": b,
    }


def map_booking_to_block(b, room_id):
    return {
        "room_id": room_id,
        "start_date": b["arrival"],
        "end_date": b["departure"],
        "reason": "Beds24 block",
        "source": "beds24",
    }
