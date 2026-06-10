#!/bin/bash
set -e
DAY=$1; CAM=$2; ANG=$3
OFFSET=${4:-61.7}
INTERVAL=${5:-1}
GPX=${6:-/srv/teslacam/gps/merged-all.gpx}
SRC=/srv/teslacam/RecentClips/$DAY
WORK=/srv/teslacam/work/$DAY/$CAM
echo "=== $DAY $CAM (angle $ANG, offset $OFFSET, interval $INTERVAL) ==="
mkdir -p "$WORK/vids"
if ! ls "$WORK/vids"/*-$CAM.mp4 >/dev/null 2>&1; then
  ln -f "$SRC"/*-$CAM.mp4 "$WORK/vids/"
fi
mapillary_tools sample_video "$WORK/vids" "$WORK/frames" \
  --video_sample_distance -1 --video_sample_interval "$INTERVAL" --rerun --skip_sample_errors
find "$WORK/frames" -mindepth 2 -name '*.jpg' -exec mv -t "$WORK/frames" {} +
find "$WORK/frames" -mindepth 1 -type d -empty -delete
mapillary_tools process "$WORK/frames" \
  --geotag_source gpx --geotag_source_path "$GPX" \
  --interpolation_offset_time "$OFFSET" --offset_angle="$ANG" \
  --device_make "Tesla" --device_model "2024 Model Y" \
  --duplicate_distance 1.5 --duplicate_angle 360 \
  --cutoff_time 600 --cutoff_distance 100 --skip_process_errors
python3 ~/teslamap/speedfilter.py "$DAY" "$CAM" "$OFFSET"
python3 ~/teslamap/distfilter.py "$DAY" "$CAM"
python3 ~/teslamap/seqfilter.py "$DAY" "$CAM"
if [ "${NOUPLOAD:-0}" != "1" ]; then
  mapillary_tools upload "$WORK/frames"
fi
