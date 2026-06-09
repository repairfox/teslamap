#!/bin/bash
source ~/map-venv/bin/activate
TODAY=$(date -u +%F)
for d in $(ls /srv/teslacam/RecentClips 2>/dev/null | sort); do
  [ "$d" = "$TODAY" ] && continue
  [ -f /srv/teslacam/processed/$d ] && continue
  ls /srv/teslacam/RecentClips/$d/*.mp4 >/dev/null 2>&1 || continue
  echo "=== $(date) processing $d ==="
  bash ~/teslamap/runday.sh "$d"
done
