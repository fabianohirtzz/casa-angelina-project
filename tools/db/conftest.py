import pytest
from apply import db_url
import psycopg2


@pytest.fixture
def conn():
    c = psycopg2.connect(db_url(), connect_timeout=20)
    try:
        yield c
    finally:
        c.rollback()
        c.close()
