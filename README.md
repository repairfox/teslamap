# teslamap

Turns archived Tesla dashcam clips + a GPS track into geotagged, filtered
[Mapillary](https://www.mapillary.com/) uploads, with per-road de-duplication so
the same roads aren't re-uploaded endlessly.

This repo is the **Pi 5 processing/upload side**. The capture side (a Pi Zero 2 W
in the car recording 6 cameras + logging GPX, then rsyncing to the Pi 5 over home
Wi-Fi) is a separate project and is assumed to already be working.

## How it works

RecentClips/<day>/*.mp4 (6 cameras recorded, 5 uploaded - rear omitted; 1-min
segments, UTC creation_time) and gps/track-*.gpx (GPS UTC, the authoritative
clock) are merged into merged-all.gpx, then process_day.py gates each clip
(bad? night? rain? already-covered?), extracts and geotags frames via runcam.sh,
runs speed / distance / sequence filters, uploads to Mapillary, records coverage,
and reclaims disk. A single corrupt clip is skipped, not fatal.

## Per-camera tuning (config.py)

Each of the 5 uploaded cameras is tuned independently:
- **CAMERAS** - heading offset (deg) added to GPS travel bearing. Front 0;
  pillars -60/+60 (10/2 o'clock); repeaters -150/+150 (7/5 o'clock).
- **SAMPLE_INTERVAL** - seconds between raw extracted frames (0.3 for all).
- **METERS_PER_FRAME** - distance-thinning target; front 7 m, sides 6 m. This is
  the real control of frame density / views-per-object / viewer smoothness.
- **OFFSET_ADJUST** - per-camera geotag time nudge (s) on top of the base offset;
  sides -1.75 to correct a ~90 ft plotting lag, front 0.

SAMPLE_INTERVAL just needs to be tight enough to hit METERS_PER_FRAME at speed;
distfilter does the precise spacing afterward.

## Filtering stages

**Clip level (before extraction, to save compute):**
- **Bad clip** - skip clips whose metadata ffprobe can't read (corrupt/truncated).
- **Night** - drop if sun elevation <= SUN_MIN_ELEVATION at clip midpoint (astral).
- **Rain** - drop if hourly precip > RAIN_THRESHOLD_MM (Open-Meteo forecast API).
- **Coverage dedup** - skip if every geohash-8 cell the clip spans is "maxed".
- **Rear redundancy** - (only if rear enabled) skip if opposite travel direction
  already has recent front coverage.

**Frame level (after extraction):**
- **Speed / parked** (speedfilter.py) - windowed GPS speed between THRESH
  (2.5 m/s) and MAXSPEED (40.23 m/s), plus density and straightness checks.
- **Distance thinning** (distfilter.py) - keep one frame per METERS_PER_FRAME
  along the geotagged track, per camera.
- **Optional home geofence** - set HOME_* coords and HOME_RADIUS_M > 0.
- **Min sequence length** (seqfilter.py) - drop sequences with < 5 frames.
- **Mapillary dedup** - --duplicate_distance 1.5, a safety floor below the
  tightest target so it only catches accidental bunching (e.g. stop-and-go).

## Coverage / de-dup rule

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

- Base timing offset ~61.7 s between Tesla video clock and GPS;
  per-camera OFFSET_ADJUST fine-tunes each camera on top of that.
- Headings, frame density, and offsets in config.py are tuned by eye on
  Mapillary after each upload - re-check after any camera mount change.
- Rear camera intentionally omitted (redundant with opposing front).
- A single corrupt clip is skipped, not fatal - the day still completes.
- Privacy: if you enable the home geofence, real coords go in config.py.
  Don't commit real coordinates to a public repo.
