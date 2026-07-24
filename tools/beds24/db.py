import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "db"))
from apply import db_url  # noqa: E402
import psycopg2  # noqa: E402


def connect():
    return psycopg2.connect(db_url(), connect_timeout=20)
