def test_can_connect_and_query(conn):
    with conn.cursor() as cur:
        cur.execute("select 1")
        assert cur.fetchone()[0] == 1
