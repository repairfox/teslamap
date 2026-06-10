import sys, json, shutil, math
from datetime import datetime
from collections import defaultdict
from config import METERS_PER_FRAME

DAY = sys.argv[1]
CAM = sys.argv[2]
TARGET = METERS_PER_FRAME.get(CAM, 5.0)

JSON = f"/srv/teslacam/work/{DAY}/{CAM}/frames/mapillary_image_description.json"


def hav(a, b, c, d):
    R = 6371000
    p1, p2 = math.radians(a), math.radians(c)
    dphi = math.radians(c - a)
    dl = math.radians(d - b)
    h = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(h))

def t(d):
    return datetime.strptime(d["MAPCaptureTime"], "%Y_%m_%d_%H_%M_%S_%f")

data = json.load(open(JSON))
ready = [d for d in data if d.get("MAPLatitude") is not None]
seqs = defaultdict(list)
for d in ready:
    seqs[d.get("MAPSequenceUUID")].append(d)
keep_ids = set()
kept = 0
for frames in seqs.values():
    frames.sort(key=t)
    last = None
    for d in frames:
        if last is None or hav(last[0], last[1],
                               d["MAPLatitude"], d["MAPLongitude"]) >= TARGET:
            keep_ids.add(id(d))
            last = (d["MAPLatitude"], d["MAPLongitude"])
            kept += 1

keep = [d for d in data
        if d.get("MAPLatitude") is None or id(d) in keep_ids]
shutil.copy(JSON, JSON + ".distbak")
json.dump(keep, open(JSON, "w"))
print(f"dist thin [{CAM}] target {TARGET} m: kept {kept}, "
      f"dropped {len(ready) - kept}")

keep = [d for d in data
        if d.get("MAPLatitude") is None or id(d) in keep_ids]
shutil.copy(JSON, JSON + ".distbak")
json.dump(keep, open(JSON, "w"))
print(f"dist thin [{CAM}] target {TARGET} m: kept {kept}, "
      f"dropped {len(ready) - kept}")
