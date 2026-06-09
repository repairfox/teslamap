import re, bisect, math
from datetime import datetime
import pygeohash
from config import GEOHASH_PRECISION

_TRKPT = re.compile(
    r'<trkpt[^>]*lat="([-0-9.]+)"[^>]*lon="([-0-9.]+)".*?<time>([^<]+)</time>',
    re.S)

def _to_epoch(s):
    s = s.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(s).timestamp()

def load_gpx_points(paths):
    pts = {}
    for p in paths:
        with open(p, errors="replace") as fh:
            data = fh.read()
        for lat, lon, t in _TRKPT.findall(data):
            try:
                e = _to_epoch(t)
            except ValueError:
                continue
            pts[e] = (e, float(lat), float(lon))
    return [pts[k] for k in sorted(pts)]

def bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

def interpolate(points, t):
    if not points or t < points[0][0] or t > points[-1][0]:
        return None
    times = [p[0] for p in points]
    i = bisect.bisect_left(times, t)
    if i == 0:
        a, b = points[0], points[1]
    elif i >= len(points):
        a, b = points[-2], points[-1]
    else:
        a, b = points[i-1], points[i]
    span = b[0] - a[0]
    f = 0 if span == 0 else (t - a[0]) / span
    lat = a[1] + (b[1]-a[1])*f
    lon = a[2] + (b[2]-a[2])*f
    brg = bearing(a[1], a[2], b[1], b[2])
    return lat, lon, brg

def geohash(lat, lon):
    return pygeohash.encode(lat, lon, precision=GEOHASH_PRECISION)

def cells_for_span(points, t0, t1, step=2.0):
    cells = []
    t = t0
    while t <= t1:
        r = interpolate(points, t)
        if r:
            lat, lon, brg = r
            cells.append((geohash(lat, lon), brg))
        t += step
    return cells
