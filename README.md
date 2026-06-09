# teslamap

Turns archived Tesla dashcam clips + a GPS track into geotagged, filtered
[Mapillary](https://www.mapillary.com/) uploads, with per-road de-duplication so
the same roads aren't re-uploaded endlessly.

This repo is the **Pi 5 processing/upload side**. The capture side (a Pi Zero 2 W
in the car recording 6 cameras + logging GPX, then rsyncing to the Pi 5 over home
Wi-Fi) is a separate project and is assumed to already be working.

## How it works

RecentClips/<day>/*.mp4 (6 cameras, 1-min segments, UTC creation_time) and
gps/track-*.gpx (GPS UTC, the authoritative clock) are merged into merged-all.gpx,
then process_day.py gates each clip (night? rain? already-covered?), extracts and
geotags frames via runcam.sh, runs speed/sequence filters, uploads to Mapillary,
records coverage, and reclaims disk.

### Filtering stages
**Clip level (before extraction, to save compute):**
- **Night** - drop if sun elevation <= SUN_MIN_ELEVATION at the clip midpoint (astral).
- **Rain** - drop if hourly precip > RAIN_THRESHOLD_MM (Open-Meteo forecast API).
- **Coverage dedup** - skip if every geohash-8 cell the clip spans is "maxed".
- **Rear redundancy** - (only if rear camera enabled) skip if opposite travel
  direction already has recent front coverage.

**Frame level (after extraction):**
- **Speed / parked** (speedfilter.py) - windowed GPS speed between THRESH
  (2.5 m/s) and MAXSPEED (40.23 m/s), plus density and path-straightness checks.
- **Optional home geofence** - set HOME_* coords and HOME_RADIUS_M > 0.
- **Min sequence length** (seqfilter.py) - drop sequences with < 5 frames.

### Coverage / de-dup rule
Key = (geohash-8 cell ~38 m, travel bearing), direction-aware (BEARING_TOL_DEG 60).
2 free uploads on a never-seen cell-direction, then 1 upload per
DEDUP_COOLDOWN_DAYS (60). Recorded only on confirmed upload.

## Setup
    python3 -m venv ~/map-venv
    source ~/map-venv/bin/activate
    pip install -r requirements.txt
    mapillary_tools authenticate
    sudo apt install ffmpeg

## Usage
    source ~/map-venv/bin/activate
    python3 merge_gpx.py /srv/teslacam/gps/merged-all.gpx /srv/teslacam/gps/track-*.gpx
    python3 process_day.py 2026-06-04 --gate-only        # dry run
    python3 process_day.py 2026-06-04 --cameras front --no-upload
    bash runday.sh 2026-06-05                            # full lifecycle
    python3 backfill_coverage.py 2026-06-03 2026-06-04   # seed DB w/o upload

### Automation
auto.sh processes every archived day that isn't marked done and isn't today.
Schedule after the overnight transfer:
    0 8 * * * /bin/bash ~/teslamap/auto.sh >> ~/teslamap/auto.log 2>&1

## Notes
- Timing offset ~61.7 s between Tesla video clock and GPS.
- Camera heading offsets in config.CAMERAS are tuned by eye on Mapillary.
- Rear camera intentionally omitted (redundant with opposing front).
- Privacy: if you enable the home geofence, real coords go in config.py.
  Don't commit real coordinates to a public repo.
