import sys, json, shutil
from collections import Counter
DAY=sys.argv[1]
CAM=sys.argv[2]
MIN=5
JSON=f"/srv/teslacam/work/{DAY}/{CAM}/frames/mapillary_image_description.json"
data=json.load(open(JSON))
ready=[d for d in data if d.get("MAPLatitude") is not None]
counts=Counter(d.get("MAPSequenceUUID") for d in ready)
print(f"{len(counts)} sequences; sizes: {sorted(counts.values(),reverse=True)[:20]}")
keep=[d for d in data if d.get("MAPLatitude") is None or counts.get(d.get("MAPSequenceUUID"),0)>=MIN]
dropped=len(ready)-sum(1 for d in keep if d.get("MAPLatitude") is not None)
shutil.copy(JSON, JSON+".seqbak")
json.dump(keep, open(JSON,"w"))
print(f"dropped {dropped} frames in sequences smaller than {MIN}")
