import os, glob, subprocess, json, time, argparse, shutil
from datetime import datetime, timezone

import geo, filters, db
from config import RECENTCLIPS, WORK_DIR, MASTER_GPX
from config import CAMERAS, DB_PATH, BEARING_TOL_DEG, SAMPLE_INTERVAL
from config import DEDUP_BURST, DEDUP_COOLDOWN_DAYS
from config import REAR_SKIP_DAYS
from clips import clip_window, list_clips

def gate_clip(path, pts, con, cam, now_ts):
    win = clip_window(path)
    if win is None:
        return ("skip", "bad_clip", 0)
    t0, dur = win
    mid_t = t0 + dur / 2.0
    mid = geo.interpolate(pts, mid_t)

    if mid is None:
        return ("skip", "no_gps", t0)

    lat, lon, _ = mid

    if not filters.is_daylight(lat, lon, mid_t):
        return ("skip", "night", t0)

    if not filters.is_dry(lat, lon, mid_t):
        return ("skip", "rain", t0)

    cells = geo.cells_for_span(pts, t0, t0 + dur)
    if not cells:
        return ("skip", "no_gps", t0)

    if all(db.is_maxed(con, gh, brg, now_ts,
                       BEARING_TOL_DEG, DEDUP_BURST,
                       DEDUP_COOLDOWN_DAYS)
           for gh, brg in cells):
        return ("skip", "covered", t0)

    if cam == "back" and all(
        db.opposing_recent(con, gh, brg, now_ts,
                           BEARING_TOL_DEG, REAR_SKIP_DAYS)
        for gh, brg in cells):
        return ("skip", "rear_redundant", t0)

    return ("process", "ok", t0)

def process_camera(day, cam, pts, con, now_ts, args):
    angle = CAMERAS[cam]
    vids = f"{WORK_DIR}/{day}/{cam}/vids"
    os.makedirs(vids, exist_ok=True)

    for f in glob.glob(f"{vids}/*.mp4"):
        os.remove(f)

    clips = list_clips(day, cam)
    if args.test:
        clips = clips[:args.test]

    reasons = {}
    kept = []

    for path in clips:
        action, reason, _ = gate_clip(path, pts, con, cam, now_ts)
        reasons[reason] = reasons.get(reason, 0) + 1

        if action == "process":
            dst = f"{vids}/{os.path.basename(path)}"
            if os.path.exists(dst):
                os.remove(dst)
            os.link(path, dst)
            kept.append(path)
        elif args.delete_rejected:
            os.remove(path)

    print(f"[{cam}] {len(clips)} clips -> {len(kept)} process; {reasons}")

    if not kept or args.gate_only:
        return

    env = dict(os.environ)
    if args.no_upload:
        env["NOUPLOAD"] = "1"

    interval = SAMPLE_INTERVAL.get(cam, 1.0)
    subprocess.run([
        "bash", os.path.expanduser("~/teslamap/runcam.sh"),
        day, cam, str(angle), str(args.offset), str(interval)
    ], check=True, env=env)

    if args.delete_source:
        for f in glob.glob(f"{vids}/*.mp4"):
            os.remove(f)

        for path in kept:
            if os.path.exists(path):
                os.remove(path)

def record_front_coverage(day, con):
    jpath = f"{WORK_DIR}/{day}/front/frames/mapillary_image_description.json"

    if not os.path.exists(jpath):
        print("no front JSON; nothing recorded")
        return

    data = json.load(open(jpath))
    seen = set()
    n = 0

    for d in data:
        if d.get("MAPLatitude") is None:
            continue

        hd = d.get("MAPCompassHeading", {}).get("TrueHeading")
        if hd is None:
            continue

        gh = geo.geohash(d["MAPLatitude"], d["MAPLongitude"])
        key = (gh, round(hd / 90.0) % 4, d.get("MAPSequenceUUID"))

        if key in seen:
            continue

        seen.add(key)

        ts = datetime.strptime(
            d["MAPCaptureTime"],
            "%Y_%m_%d_%H_%M_%S_%f"
        ).replace(tzinfo=timezone.utc).timestamp()

        db.record(con, gh, hd, ts)
        n += 1

    print(f"recorded {n} front coverage rows")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("day")
    ap.add_argument("--cameras", default=",".join(CAMERAS))
    ap.add_argument("--offset", type=float, default=61.7)
    ap.add_argument("--test", type=int, default=0)
    ap.add_argument("--gate-only", action="store_true")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--delete-rejected", action="store_true")
    ap.add_argument("--delete-source", action="store_true")
    ap.add_argument("--no-record", action="store_true")

    args = ap.parse_args()

    pts = geo.load_gpx_points([MASTER_GPX])
    print(f"loaded {len(pts)} gpx points")

    con = db.connect(DB_PATH)
    now_ts = time.time()
    cams = args.cameras.split(",")

    for cam in cams:
        process_camera(args.day, cam, pts, con, now_ts, args)

    should_record = (
        not args.no_record
        and not args.gate_only
        and not args.no_upload
        and "front" in cams
    )

    if should_record:
        record_front_coverage(args.day, con)

    if args.delete_source and not args.gate_only:
        for cam in cams:
            shutil.rmtree(
                f"{WORK_DIR}/{args.day}/{cam}/frames",
                ignore_errors=True
            )
        shutil.rmtree(
            f"{RECENTCLIPS}/{args.day}",
            ignore_errors=True
        )

if __name__ == "__main__":
    main()

def gate_clip(path, pts, con, cam, now_ts):
    win = clip_window(path)
    if win is None:
        return ("skip", "bad_clip", 0)
    t0, dur = win
    mid_t = t0 + dur / 2.0
    mid = geo.interpolate(pts, mid_t)
    if mid is None:
        return ("skip", "no_gps", t0)
    lat, lon, _ = mid
    if not filters.is_daylight(lat, lon, mid_t):
        return ("skip", "night", t0)
    if not filters.is_dry(lat, lon, mid_t):
        return ("skip", "rain", t0)
    cells = geo.cells_for_span(pts, t0, t0 + dur)
    if not cells:
        return ("skip", "no_gps", t0)
    if all(db.is_maxed(con, gh, brg, now_ts, BEARING_TOL_DEG,
                       DEDUP_BURST, DEDUP_COOLDOWN_DAYS) for gh, brg in cells):
        return ("skip", "covered", t0)
    if cam == "back" and all(
        db.opposing_recent(con, gh, brg, now_ts, BEARING_TOL_DEG, REAR_SKIP_DAYS)
        for gh, brg in cells):
        return ("skip", "rear_redundant", t0)
    return ("process", "ok", t0)
