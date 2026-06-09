import subprocess, json, glob
from datetime import datetime
from config import RECENTCLIPS

def clip_window(path):
    """Return (start_epoch_utc, duration_sec) from embedded metadata."""
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_entries", "format_tags=creation_time:format=duration", path],
        capture_output=True, text=True).stdout
    j = json.loads(out)
    ct = j["format"]["tags"]["creation_time"]
    dur = float(j["format"].get("duration", 60) or 60)
    e = datetime.fromisoformat(ct.replace("Z", "+00:00")).timestamp()
    return e, dur

def list_clips(day, camera):
    return sorted(glob.glob(f"{RECENTCLIPS}/{day}/*-{camera}.mp4"))
