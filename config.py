# ---- paths ----
RECENTCLIPS = "/srv/teslacam/RecentClips"
GPS_DIR     = "/srv/teslacam/gps"
WORK_DIR    = "/srv/teslacam/work"
DB_PATH     = "/srv/teslacam/coverage.db"

# ---- cameras: name -> heading offset (deg) added to travel bearing ----
CAMERAS = {
    "front":          0,
    "left_pillar":   -60,
    "right_pillar":   60,
    "left_repeater": -150,
    "right_repeater": 150,
}

# ---- timing ----
TZ_LOCAL        = "America/New_York"   # Tesla filename tz (EDT/EST)
SAMPLE_INTERVAL = 1.0                  # fps = 1/this

# ---- coverage / dedup ----
GEOHASH_PRECISION = 8        # ~38 m cells
BEARING_TOL_DEG   = 60       # same-direction tolerance
MAX_PER_WINDOW    = 2        # max uploads per cell-direction...
WINDOW_DAYS       = 30       # ...within this trailing window

# ---- night ----
SUN_MIN_ELEVATION = 0.0      # deg above horizon; raise to 3 if low-sun glare

# ---- weather ----
RAIN_THRESHOLD_MM = 0.1      # hourly precip above this = skip
WEATHER_PAST_DAYS = 3        # Open-Meteo forecast API past_days window

# --- dedup / camera-skip rules ---
DEDUP_BURST = 2            # free uploads on a never-maxed cell-direction
DEDUP_COOLDOWN_DAYS = 60   # then 1 per this many days
REAR_SKIP_DAYS = 60        # skip rear cam if opposing front coverage within N days
MASTER_GPX = "/srv/teslacam/gps/merged-all.gpx"

SAMPLE_INTERVAL = {
    "front":          0.3,
    "left_pillar":    0.3,
    "right_pillar":   0.3,
    "left_repeater":  0.3,
    "right_repeater": 0.3,
}

METERS_PER_FRAME = {
    "front":          7.0,
    "left_pillar":    4.5,
    "right_pillar":   4.5,
    "left_repeater":  6.0,
    "right_repeater": 6.0,
}

OFFSET_ADJUST = {
    "front":          0.0,
    "left_pillar":   -1.5,
    "right_pillar":  -1.5,
    "left_repeater": -1.5,
    "right_repeater": -1.5,
}
