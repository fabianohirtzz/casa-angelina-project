import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from auth import get_access_token
from client import Beds24Client

OUT = os.path.join(os.path.dirname(__file__), "fixtures")


def main():
    os.makedirs(OUT, exist_ok=True)
    client = Beds24Client(get_access_token())
    props = client.get_properties()
    with open(os.path.join(OUT, "properties.json"), "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)
    bookings = client.get_bookings()
    with open(os.path.join(OUT, "bookings.json"), "w", encoding="utf-8") as f:
        json.dump(bookings[:10], f, ensure_ascii=False, indent=2)
    print(f"properties: {len(props)}; bookings capturados: {len(bookings)}")
    if props:
        print("roomTypes:", [rt.get("name") for rt in (props[0].get("roomTypes") or [])])
    if bookings:
        print("campos do 1o booking:", sorted(bookings[0].keys()))


if __name__ == "__main__":
    main()
