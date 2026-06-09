# ---- paths ----
RECENTCLIPS = "/srv/teslacam/RecentClips"
GPS_DIR     = "/srv/teslacam/gps"
WORK_DIR    = "/srv/teslacam/work"
DB_PATH     = "/srv/teslacam/coverage.db"

# ---- cameras: name -> heading offset (deg) added to travel bearing ----
CAMERAS = {
    "front":          0,
    "left_pillar":   -45,
    "right_pillar":   45,
    "left_repeater": -120,
    "right_repeater": 120,
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
