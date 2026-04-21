#!/usr/bin/env bash
set -euo pipefail

LOG=/tmp/kiosk.log
exec > >(tee -a "$LOG") 2>&1
echo "=== start-kiosk.sh $(date) ==="
set -x

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$REPO_DIR/venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$REPO_DIR/venv/bin/activate"
fi

OUTPUT="HDMI-2"
OTHER_OUTPUT="HDMI-1"
ROTATION="left"
URL="http://localhost:4200"

echo "---- xrandr -q (before) ----"
xrandr -q || true
echo "---- /xrandr -q ----"
xrandr --output "$OTHER_OUTPUT" --off || true
xrandr --output "$OUTPUT" --rotate "$ROTATION"
read W H < <(xrandr | awk -v out="$OUTPUT" '$1==out && $2=="connected" {
  for (i=3;i<=NF;i++) if ($i ~ /[0-9]+x[0-9]+\+/) { split($i,a,"[x+]"); print a[1], a[2]; exit }
}')
xset s off
xset -dpms
xset s noblank

cd "$REPO_DIR/display/frontend"
npm start -- --host 0.0.0.0 --port 4200 &
NG_PID=$!

cd "$REPO_DIR/display"
uvicorn server:app --host 0.0.0.0 --port 8000 &
UV_PID=$!

cleanup() { kill "$NG_PID" "$UV_PID" 2>/dev/null || true; }
trap cleanup EXIT

until curl -fsS http://localhost:4200 >/dev/null 2>&1; do sleep 1; done
until curl -fsS http://localhost:8000 >/dev/null 2>&1; do sleep 1; done

exec chromium-browser \
  --kiosk \
  --window-size="${W},${H}" \
  --window-position=0,0 \
  --noerrdialogs \
  --disable-session-crashed-bubble \
  --disable-infobars \
  "$URL"
