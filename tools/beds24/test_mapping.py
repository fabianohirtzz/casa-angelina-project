import pytest
import mapping


def _booking(**over):
    b = {
        "id": 555,
        "propertyId": 1,
        "roomId": 99,
        "status": "confirmed",
        "arrival": "2026-02-10",
        "departure": "2026-02-14",
        "numAdult": 2,
        "numChild": 0,
        "firstName": "Ana",
        "lastName": "Silva",
        "email": "ana@x.com",
        "phone": "5573999",
        "country": "BR",
        "price": "1584.00",
        "apiSourceId": 19,
        "masterId": 555,
        "modifiedTime": "2026-01-20 10:00:00",
    }
    b.update(over)
    return b


def test_map_status_variants():
    assert mapping.map_status("New") == "confirmed"
    assert mapping.map_status("CONFIRMED") == "confirmed"
    assert mapping.map_status("Request") == "pending"
    assert mapping.map_status("inquiry") == "pending"
    assert mapping.map_status("Cancelled") == "cancelled"
    assert mapping.map_status("Black") is None


def test_is_block():
    assert mapping.is_block("black") is True
    assert mapping.is_block("Confirmed") is False


def test_map_channel():
    assert mapping.map_channel(0) == "direct"
    assert mapping.map_channel(19) == "booking"
    assert mapping.map_channel(46) == "airbnb"
    assert mapping.map_channel(123) == "manual"
    assert mapping.map_channel(None) == "manual"


def test_map_booking_to_reservation():
    row = mapping.map_booking_to_reservation(_booking(), room_id="R", guest_id="G")
    assert row["room_id"] == "R"
    assert row["guest_id"] == "G"
    assert row["beds24_booking_id"] == "555"
    assert row["group_ref"] == "555"
    assert row["channel"] == "booking"
    assert row["status"] == "confirmed"
    assert row["check_in"] == "2026-02-10"
    assert row["check_out"] == "2026-02-14"
    assert row["num_guests"] == 2
    assert str(row["total_amount"]) == "1584.00"
    assert row["beds24_modified_at"] == "2026-01-20 10:00:00"
    assert row["raw_payload"]["id"] == 555


def test_reservation_num_guests_sums_adults_and_children():
    row = mapping.map_booking_to_reservation(_booking(numAdult=2, numChild=1),
                                             room_id="R", guest_id=None)
    assert row["num_guests"] == 3
    assert row["guest_id"] is None


def test_map_booking_to_block():
    blk = mapping.map_booking_to_block(_booking(status="Black"), room_id="R")
    assert blk["room_id"] == "R"
    assert blk["start_date"] == "2026-02-10"
    assert blk["end_date"] == "2026-02-14"
    assert blk["source"] == "beds24"


def test_guest_fields():
    g = mapping.guest_fields(_booking())
    assert g["full_name"] == "Ana Silva"
    assert g["email"] == "ana@x.com"
    assert g["phone"] == "5573999"
    assert g["country"] == "BR"


def test_map_status_unknown_raises():
    with pytest.raises(ValueError):
        mapping.map_status("totally_unknown")


def test_group_ref_none_when_masterid_absent():
    row = mapping.map_booking_to_reservation(_booking(masterId=0), room_id="R", guest_id=None)
    assert row["group_ref"] is None
    b = _booking()
    del b["masterId"]
    row2 = mapping.map_booking_to_reservation(b, room_id="R", guest_id=None)
    assert row2["group_ref"] is None


def test_num_guests_none_when_zero():
    row = mapping.map_booking_to_reservation(_booking(numAdult=0, numChild=0), room_id="R", guest_id=None)
    assert row["num_guests"] is None


def test_guest_phone_falls_back_to_mobile():
    b = _booking()
    del b["phone"]
    b["mobile"] = "55MOBILE"
    g = mapping.guest_fields(b)
    assert g["phone"] == "55MOBILE"
