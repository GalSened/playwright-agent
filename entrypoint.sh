#!/usr/bin/env bash
set -e

# Optional headed mode without host X-server:
# If HEADFUL=1, start an internal virtual display (Xvfb).
if [[ "$HEADFUL" == "1" ]]; then
  echo "🖥️  Launching internal Xvfb for headed debugging..."
  export DISPLAY=:99
  Xvfb :99 -screen 0 1920x1080x24 &
else
  export HEADLESS_ENV=1
fi

exec "$@"
