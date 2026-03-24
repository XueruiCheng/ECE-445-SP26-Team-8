import json
import os

import cv2
import insightface
import numpy as np

from .settings import RAW_IMAGES_DIR, OUT_EMBEDDINGS, OUT_NAMES


def filename_to_display_name(filename: str) -> str:
    """Extract display name from files in raw_images"""
    stem = os.path.splitext(filename)[0]
    return stem.replace("_", " ").title()


def build_database():
    app = insightface.app.FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=0, det_size=(320, 320))

    embeddings = []
    names = []
    skipped = []

    image_files = sorted(
        f for f in os.listdir(RAW_IMAGES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )

    for filename in image_files:
        path = os.path.join(RAW_IMAGES_DIR, filename)
        img = cv2.imread(path)

        if img is None:
            skipped.append(filename)
            continue

        faces = app.get(img)

        if not faces:
            skipped.append(filename)
            continue

        # Take the highest-confidence face
        face = faces[0]

        if face.embedding is None:
            skipped.append(filename)
            continue

        embedding = face.embedding
        name = filename_to_display_name(filename)
        embeddings.append(embedding)
        names.append(name)

        del img

    if not embeddings:
        print("No embeddings generated")
        return

    np.save(OUT_EMBEDDINGS, np.array(embeddings, dtype=np.float32))
    with open(OUT_NAMES, "w") as f:
        json.dump(names, f, indent=2)

    if skipped:
        print(f"\nSkipped files: {skipped}")


if __name__ == "__main__":
    build_database()
