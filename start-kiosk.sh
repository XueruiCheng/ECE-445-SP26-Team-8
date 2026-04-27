#!/usr/bin/env bash
set -euo pipefail

# --- Optional: validation mode -------------------------------------
# Run `./start-kiosk.sh --validate "Avery Broderick"` to keep the
# webcam preview + thumbs-up gesture intact, but feed the face model
# a noisy version of model/data/raw_images/<name>.jpg instead of the
# user's actual face. Useful for demoing the pipeline with a known
# expected match. Noise level: VALIDATE_NOISE=mild|harsh (default harsh).
# ------------------------------------------------------------------

VALIDATE_NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --validate)
      VALIDATE_NAME="${2:-}"
      shift 2
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 1
      ;;
  esac
done
export VALIDATE_NAME

LOG=/tmp/kiosk.log
exec > >(tee -a "$LOG") 2>&1
echo "=== start-kiosk.sh $(date) VALIDATE_NAME=${VALIDATE_NAME:-<none>} ==="
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

# Hide the mouse cursor (prereq: sudo apt install -y unclutter).
unclutter -idle 0 -root &
UNCLUTTER_PID=$!

cleanup() { kill "$NG_PID" "$UV_PID" "$UNCLUTTER_PID" 2>/dev/null || true; }
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
