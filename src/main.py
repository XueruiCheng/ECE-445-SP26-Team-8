import cv2
import insightface

from face_match import load_database, find_match, MATCH_THRESHOLD

app = insightface.app.FaceAnalysis(name="buffalo_sc")
app.prepare(ctx_id=0, det_size=(320, 320))

db_embeddings, db_names = load_database()

# TODO: switch index for Logitech webcam on Pi
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = app.get(frame)

    for face in faces:
        name, score = find_match(face.embedding, db_embeddings, db_names)

        if score >= MATCH_THRESHOLD:
            cap.release()
            print(f"Matched: {name} (score: {score:.2f})")
            exit(0)

    # ESC to cancel
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
print("No confident match found.")
