import math
import random
import time
from dataclasses import dataclass

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# -----------------------------
# Config
# -----------------------------
CAMERA_ID = 0
WIDTH = 1280
HEIGHT = 720

MODEL_PATH = "hand_landmarker.task"   # put this file in the same folder
NUM_ATOMS = 1
ATOM_RADIUS = 24
SHOT_COOLDOWN = 0.40

# Trigger tuning
PINCH_PRESS_THRESHOLD = 0.050
PINCH_RELEASE_THRESHOLD = 0.075

MIN_HAND_DETECTION_CONFIDENCE = 0.6
MIN_HAND_PRESENCE_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# Aiming / target settings
AIM_LENGTH_PIXELS = 180
TARGET_SMOOTHING = 0.28
TARGET_RADIUS = 20


# -----------------------------
# Landmark indices
# -----------------------------
WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_TIP = 8
MIDDLE_MCP = 9


# -----------------------------
# Atom class
# -----------------------------
@dataclass
class Atom:
    x: float
    y: float
    vx: float
    vy: float
    radius: int = ATOM_RADIUS
    alive: bool = True

    def update(self, width: int, height: int):
        if not self.alive:
            return

        self.x += self.vx
        self.y += self.vy

        if self.x < self.radius or self.x > width - self.radius:
            self.vx *= -1
            self.x = max(self.radius, min(width - self.radius, self.x))

        if self.y < self.radius + 80 or self.y > height - self.radius:
            self.vy *= -1
            self.y = max(self.radius + 80, min(height - self.radius, self.y))

    def draw(self, frame):
        if not self.alive:
            return

        center = (int(self.x), int(self.y))
        cv2.circle(frame, center, self.radius, (255, 220, 120), 2)
        cv2.circle(frame, center, 7, (255, 220, 120), -1)
        cv2.ellipse(frame, center, (self.radius + 10, self.radius - 4), 0, 0, 360, (180, 180, 255), 1)
        cv2.ellipse(frame, center, (self.radius - 4, self.radius + 10), 60, 0, 360, (180, 180, 255), 1)

    def contains(self, px: int, py: int) -> bool:
        return (self.x - px) ** 2 + (self.y - py) ** 2 <= self.radius ** 2


# -----------------------------
# Utils
# -----------------------------
def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


def normalized_to_pixel(lm, width, height):
    return int(lm.x * width), int(lm.y * height)


def landmark_distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def create_atoms(width: int, height: int):
    atoms = []
    for _ in range(NUM_ATOMS):
        while True:
            x = random.randint(120, width - 120)
            y = random.randint(140, height - 120)
            vx = random.choice([-1, 1]) * random.uniform(2.5, 4.5)
            vy = random.choice([-1, 1]) * random.uniform(2.0, 4.0)

            good = True
            for a in atoms:
                if math.hypot(a.x - x, a.y - y) < 120:
                    good = False
                    break
            if good:
                atoms.append(Atom(x=x, y=y, vx=vx, vy=vy))
                break
    return atoms


def project_target_from_hand(lms, width, height, aim_length=AIM_LENGTH_PIXELS):
    """
    Projects a target reticle outward from the finger direction.
    Direction is based on INDEX_MCP -> INDEX_TIP.
    """
    tip = lms[INDEX_TIP]
    mcp = lms[INDEX_MCP]

    tip_x, tip_y = normalized_to_pixel(tip, width, height)
    mcp_x, mcp_y = normalized_to_pixel(mcp, width, height)

    dx = tip_x - mcp_x
    dy = tip_y - mcp_y

    mag = math.hypot(dx, dy)
    if mag < 1e-6:
        return tip_x, tip_y

    dx /= mag
    dy /= mag

    target_x = int(tip_x + dx * aim_length)
    target_y = int(tip_y + dy * aim_length)

    target_x = clamp(target_x, 0, width - 1)
    target_y = clamp(target_y, 80, height - 1)

    return target_x, target_y


def draw_target(frame, x, y, radius=TARGET_RADIUS, color=(0, 255, 255)):
    cv2.circle(frame, (x, y), radius, color, 2)
    cv2.circle(frame, (x, y), 6, color, 2)

    tick = radius + 10
    gap = radius - 4

    cv2.line(frame, (x - tick, y), (x - gap, y), color, 2)
    cv2.line(frame, (x + gap, y), (x + tick, y), color, 2)
    cv2.line(frame, (x, y - tick), (x, y - gap), color, 2)
    cv2.line(frame, (x, y + gap), (x, y + tick), color, 2)


def draw_beam(frame, start_pt, end_pt):
    cv2.line(frame, start_pt, end_pt, (255, 255, 0), 3)
    cv2.circle(frame, end_pt, 12, (255, 255, 0), 2)


def draw_hud(frame, hits, total, system_ready, trigger_down):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 80), (20, 20, 20), -1)

    cv2.putText(
        frame,
        f"Atoms hit: {hits}/{total}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2,
    )

    trigger_text = "TRIGGER: ON" if trigger_down else "TRIGGER: OFF"
    trigger_color = (0, 220, 255) if trigger_down else (160, 160, 160)
    cv2.putText(
        frame,
        trigger_text,
        (20, 68),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        trigger_color,
        2,
    )

    if system_ready:
        cv2.putText(
            frame,
            "SYSTEM INITIALIZED",
            (w // 2 - 220, 55),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            (0, 255, 120),
            3,
        )
    else:
        cv2.putText(
            frame,
            "Hit all 3 atoms to initialize",
            (w // 2 - 260, 55),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            (200, 200, 200),
            2,
        )


def create_landmarker():
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=MIN_HAND_DETECTION_CONFIDENCE,
        min_hand_presence_confidence=MIN_HAND_PRESENCE_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    )
    return vision.HandLandmarker.create_from_options(options)


def main():
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        return

    atoms = create_atoms(WIDTH, HEIGHT)
    hits = 0
    system_ready = False

    target_x = WIDTH // 2
    target_y = HEIGHT // 2

    last_shot_time = 0.0
    trigger_prev = False
    beam_until = 0.0
    beam_start = None
    beam_end = None

    last_timestamp_ms = 0

    try:
        with create_landmarker() as landmarker:
            while True:
                ok, frame = cap.read()
                if not ok:
                    print("ERROR: Failed to read frame.")
                    break

                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (WIDTH, HEIGHT))

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

                current_ts = int(time.monotonic() * 1000)
                timestamp_ms = max(current_ts, last_timestamp_ms + 1)
                last_timestamp_ms = timestamp_ms

                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                trigger_down = False
                muzzle_point = None

                if not system_ready:
                    for atom in atoms:
                        atom.update(WIDTH, HEIGHT)

                if result.hand_landmarks and len(result.hand_landmarks) > 0:
                    lms = result.hand_landmarks[0]

                    raw_target_x, raw_target_y = project_target_from_hand(lms, WIDTH, HEIGHT)
                    target_x = int(lerp(target_x, raw_target_x, TARGET_SMOOTHING))
                    target_y = int(lerp(target_y, raw_target_y, TARGET_SMOOTHING))

                    pinch_dist = landmark_distance(lms[THUMB_TIP], lms[INDEX_TIP])

                    if trigger_prev:
                        trigger_down = pinch_dist < PINCH_RELEASE_THRESHOLD
                    else:
                        trigger_down = pinch_dist < PINCH_PRESS_THRESHOLD

                    muzzle_point = normalized_to_pixel(lms[INDEX_TIP], WIDTH, HEIGHT)

                    now = time.time()
                    just_fired = trigger_down and (not trigger_prev) and (now - last_shot_time > SHOT_COOLDOWN)

                    if just_fired:
                        last_shot_time = now
                        beam_until = now + 0.10
                        beam_start = muzzle_point
                        beam_end = (target_x, target_y)

                        if not system_ready:
                            for atom in atoms:
                                if atom.alive and atom.contains(target_x, target_y):
                                    atom.alive = False
                                    hits += 1
                                    break

                            if hits >= NUM_ATOMS:
                                system_ready = True

                    trigger_prev = trigger_down
                else:
                    trigger_prev = False

                for atom in atoms:
                    atom.draw(frame)

                if beam_until > time.time() and beam_start is not None and beam_end is not None:
                    draw_beam(frame, beam_start, beam_end)

                draw_target(frame, target_x, target_y)
                draw_hud(frame, hits, NUM_ATOMS, system_ready, trigger_down)

                if system_ready:
                    cv2.putText(
                        frame,
                        "READY",
                        (WIDTH // 2 - 60, HEIGHT // 2),
                        cv2.FONT_HERSHEY_TRIPLEX,
                        2.0,
                        (0, 255, 120),
                        4,
                    )

                cv2.imshow("Quantum Atom Init", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == 27 or key == ord("q"):
                    break
                elif key == ord("r"):
                    atoms = create_atoms(WIDTH, HEIGHT)
                    hits = 0
                    system_ready = False
                    beam_until = 0.0

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()