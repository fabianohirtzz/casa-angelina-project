import sys
import psycopg2


def load_env(path=".supabaseauth"):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k] = v
    return env


def db_url():
    url = load_env()["SUPABASE_DB_URL"]
    return url + ("&" if "?" in url else "?") + "sslmode=require"


def apply_file(path):
    sql = open(path, encoding="utf-8").read()
    conn = psycopg2.connect(db_url(), connect_timeout=20)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.close()
    print("aplicado:", path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python tools/db/apply.py <arquivo.sql>")
        sys.exit(2)
    apply_file(sys.argv[1])
