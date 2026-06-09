import sys, re
pts=[]
for path in sys.argv[2:]:
    data=open(path, errors='replace').read()
    for m in re.finditer(r'<trkpt\b.*?</trkpt>', data, re.S):
        t=re.search(r'<time>([^<]+)</time>', m.group(0))
        if t: pts.append((t.group(1), m.group(0)))
pts.sort()
seen=set()
with open(sys.argv[1],'w') as out:
    out.write('<?xml version="1.0"?>\n<gpx version="1.1"><trk><trkseg>\n')
    for t,blk in pts:
        if t in seen: continue
        seen.add(t); out.write(blk+'\n')
    out.write('</trkseg></trk></gpx>\n')
