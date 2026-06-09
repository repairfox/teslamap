import sqlite3

DB_PATH = "/srv/teslacam/coverage.db"

def connect(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE IF NOT EXISTS coverage("
                 "geohash TEXT, bearing REAL, upload_ts REAL)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_gh ON coverage(geohash)")
    conn.commit()
    return conn

def _bdiff(a, b):
    d = abs(a - b) % 360.0
    return d if d <= 180 else 360 - d

def _ts_list(conn, gh, bearing, tol):
    cur = conn.execute("SELECT bearing, upload_ts FROM coverage WHERE geohash=?", (gh,))
    return [ts for (b, ts) in cur.fetchall() if _bdiff(b, bearing) <= tol]

def is_maxed(conn, gh, bearing, now_ts, tol=60, burst=2, cooldown_days=30):
    # never-maxed cell-direction gets `burst` free uploads, then 1 per cooldown
    ts_list = _ts_list(conn, gh, bearing, tol)
    if len(ts_list) < burst:
        return False
    return (now_ts - max(ts_list)) < cooldown_days * 86400

def opposing_recent(conn, gh, bearing, now_ts, tol=60, days=60):
    # rear-skip: is there front coverage of the opposite travel dir recently?
    opp = (bearing + 180.0) % 360.0
    return any((now_ts - ts) < days * 86400
               for ts in _ts_list(conn, gh, opp, tol))

def record(conn, gh, bearing, now_ts):
    conn.execute("INSERT INTO coverage(geohash,bearing,upload_ts) VALUES(?,?,?)",
                 (gh, bearing, now_ts))
    conn.commit()
