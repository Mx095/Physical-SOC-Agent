"""
Physical SOC Agent — main entry point.

Run with:
    python agent.py

Requires owner_face.npy to exist first — run enroll_owner.py once before
running this.

State machine, evaluated once per frame:
    owner present               -> NORMAL, reset all counters
    owner absent past threshold -> lock the session
    any stranger face present   -> log an alert (rate-limited)
Both checks run independently, so a stranger sitting down while you're
still in frame is caught too, not just an empty chair.
"""
import os
import time
import cv2
import numpy as np

import config
from face_id import detect_faces, get_embedding, is_owner, draw_faces
from session_lock import lock_session
from db import insert_event

os.makedirs(config.SNAPSHOT_DIR, exist_ok=True)

if not os.path.exists("owner_face.npy"):
    raise SystemExit("[!] owner_face.npy not found. Run 'python enroll_owner.py' first.")

OWNER_EMBEDDING = np.load("owner_face.npy")


def save_snapshot(frame) -> str:
    filename = f"{config.SNAPSHOT_DIR}/breach_{int(time.time())}.jpg"
    cv2.imwrite(filename, frame)
    return filename


def main():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        print("[!] Could not open webcam. Check CAMERA_INDEX in config.py")
        return

    owner_absent_since = None
    last_alert_time = 0.0
    locked = False

    print("[*] Physical SOC Agent running. Press Ctrl+C (or 'q') to stop.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            faces = detect_faces(frame)
            now = time.time()

            labels = []
            owner_present = False
            stranger_present = False

            for face in faces:
                embedding = get_embedding(frame, face)
                if is_owner(embedding, OWNER_EMBEDDING):
                    labels.append("OWNER")
                    owner_present = True
                else:
                    labels.append("STRANGER")
                    stranger_present = True

            if owner_present:
                owner_absent_since = None
                locked = False
            else:
                if owner_absent_since is None:
                    owner_absent_since = now
                elif (now - owner_absent_since) >= config.NO_FACE_LOCK_SECONDS and not locked:
                    snapshot = save_snapshot(frame)
                    insert_event("session_lock", "warning",
                                 "Owner not detected — session locked", snapshot)
                    lock_session()
                    locked = True
                    print("[LOCK] Owner not detected — session locked.")

            if stranger_present:
                if now - last_alert_time >= config.SECOND_FACE_COOLDOWN:
                    snapshot = save_snapshot(frame)
                    insert_event("unauthorized_face", "critical",
                                 "Unrecognized face detected in frame", snapshot)
                    last_alert_time = now
                    print("[ALERT] Unrecognized face detected.")

            if config.SHOW_PREVIEW_WINDOW:
                draw_faces(frame, faces, labels)
                cv2.imshow("Physical SOC Agent (press q to quit)", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        print("\n[*] Stopping agent.")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
