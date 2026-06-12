import requests
from datetime import datetime, timezone
from astral import Observer
from astral.sun import elevation
from config import SUN_MIN_ELEVATION, RAIN_THRESHOLD_MM, WEATHER_PAST_DAYS


def is_daylight(lat, lon, t_epoch):
    dt = datetime.fromtimestamp(t_epoch, tz=timezone.utc)
    return elevation(Observer(lat, lon), dt) > SUN_MIN_ELEVATION


_weather_cache = {}


def is_dry(lat, lon, t_epoch):
    dt = datetime.fromtimestamp(t_epoch, tz=timezone.utc)
    hour = dt.strftime("%Y-%m-%dT%H:00")
    key = (round(lat, 1), round(lon, 1), hour)
    if key not in _weather_cache:
        try:
            r = requests.get("https://api.open-meteo.com/v1/forecast", params={
                "latitude": round(lat, 2), "longitude": round(lon, 2),
                "hourly": "precipitation", "past_days": WEATHER_PAST_DAYS,
                "timezone": "UTC"}, timeout=15)
            d = r.json()["hourly"]
            for tt, pp in zip(d["time"], d["precipitation"]):
                _weather_cache[(round(lat, 1), round(lon, 1), tt)] = pp or 0.0
        except Exception:
            return True
    precip = _weather_cache.get(key, 0.0)
    return precip <= RAIN_THRESHOLD_MM
