#!/bin/sh
set -eu

data="${GARMINTOKENS:-/data}"
mkdir -p "$data"

if [ -f "$data/garmin_tokens.txt" ] && [ ! -s "$data/garmin_tokens.json" ]; then
  cp "$data/garmin_tokens.txt" "$data/garmin_tokens.json"
fi

# RouterOS FTP bind-mounts are root-owned. chmod so the process can read them.
# Do not drop privileges: chown on these mounts often fails.
for f in "$data/garmin_tokens.json" "$data/garmin_tokens.txt"; do
  if [ -f "$f" ]; then
    chmod 600 "$f" 2>/dev/null || true
  fi
done
chmod 700 "$data" 2>/dev/null || true

exec "$@"
