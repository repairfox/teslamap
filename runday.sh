#!/bin/bash
set -e
DAY=$1
[ -z "$DAY" ] && { echo "ERROR: no day given"; exit 1; }
cd ~/teslamap
source ~/map-venv/bin/activate
python3 merge_gpx.py /srv/teslacam/gps/merged-all.gpx /srv/teslacam/gps/track-*.gpx
python3 process_day.py "$DAY" --delete-rejected --delete-source
mkdir -p /srv/teslacam/processed && touch /srv/teslacam/processed/$DAY
