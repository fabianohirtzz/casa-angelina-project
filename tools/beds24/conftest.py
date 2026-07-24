import pytest
from db import connect


@pytest.fixture
def conn():
    c = connect()
    try:
        yield c
    finally:
        c.rollback()
        c.close()
