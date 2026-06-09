import json, re, math, bisect, shutil, sys
from datetime import datetime, timedelta
DAY    = sys.argv[1]
CAM    = sys.argv[2]
OFFSET = float(sys.argv[3]) if len(sys.argv) > 3 else 63.0
GPX    = sys.argv[4] if len(sys.argv) > 4 else "/srv/teslacam/gps/merged-all.gpx"
MAXSPEED = 40.23   # >90 mph
THRESH   = 1.5     # m/s; below = parked/crawl
WIN      = 10      # +/- seconds
MINPTS   = 8       # require this many gpx points in window, else drop
MINDT    = 12      # window must span at least this many seconds, else drop
JSON = f"/srv/teslacam/work/{DAY}/{CAM}/frames/mapillary_image_description.json"
gpx=[]
for la,lo,t in re.findall(r'<trkpt lat="([^"]+)" lon="([^"]+)">.*?<time>([^<]+)</time>',open(GPX).read(),re.S):
    gpx.append((datetime.strptime(t,"%Y-%m-%dT%H:%M:%S.%fZ"),float(la),float(lo)))
gpx.sort()
times=[p[0] for p in gpx]
def hav(a,b,c,d):
    R=6371000; p1,p2=math.radians(a),math.radians(c)
    dphi=math.radians(c-a); dl=math.radians(d-b)
    h=math.sin(dphi/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))
def window_speed(tt):
    lo=bisect.bisect_left(times, tt-timedelta(seconds=WIN))
    hi=bisect.bisect_right(times, tt+timedelta(seconds=WIN))
    w=gpx[lo:hi]
    if len(w) < MINPTS:
        return None
    dt=(w[-1][0]-w[0][0]).total_seconds()
    if dt < MINDT:
        return None
    return hav(w[0][1],w[0][2],w[-1][1],w[-1][2])/dt
data=json.load(open(JSON))
kept=[]; dropped=0
for d in data:
    if d.get("MAPLatitude") is None:
        kept.append(d); continue
    t=datetime.strptime(d["MAPCaptureTime"],"%Y_%m_%d_%H_%M_%S_%f")+timedelta(seconds=OFFSET)
    s=window_speed(t)
    if s is None or s < THRESH or s > MAXSPEED: dropped+=1
    else: kept.append(d)
shutil.copy(JSON, JSON+".bak")
json.dump(kept, open(JSON,"w"))
print(f"dropped {dropped}; {sum(1 for k in kept if k.get('MAPLatitude'))} remain")
