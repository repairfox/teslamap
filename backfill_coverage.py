import sys, math
from datetime import datetime, timezone
import geo, filters, db
from config import MASTER_GPX, DB_PATH
DATES=set(sys.argv[1:])
if not DATES:
    print("usage: backfill_coverage.py YYYY-MM-DD [...]"); sys.exit(1)
GAP=600; MOVE=2.5
def hav(a,b,c,d):
    R=6371000;p1,p2=math.radians(a),math.radians(c)
    dphi=math.radians(c-a);dl=math.radians(d-b)
    h=math.sin(dphi/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))
pts=geo.load_gpx_points([MASTER_GPX]); con=db.connect(DB_PATH)
drives=[]; cur=[pts[0]]
for p in pts[1:]:
    if p[0]-cur[-1][0]>GAP: drives.append(cur); cur=[p]
    else: cur.append(p)
drives.append(cur)
rec=0
for dr in drives:
    seen=set()
    for i in range(1,len(dr)):
        e,la,lo=dr[i]; pe,pla,plo=dr[i-1]
        if datetime.fromtimestamp(e,tz=timezone.utc).strftime("%Y-%m-%d") not in DATES: continue
        dt=e-pe
        if dt<=0 or hav(pla,plo,la,lo)/dt < MOVE: continue
        if not filters.is_daylight(la,lo,e): continue
        brg=geo.bearing(pla,plo,la,lo); gh=geo.geohash(la,lo)
        k=(gh,round(brg/90.0)%4)
        if k in seen: continue
        seen.add(k); db.record(con,gh,brg,e); rec+=1
print("recorded",rec,"cells for",sorted(DATES))
