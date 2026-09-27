"""
Run this ONCE, before agent.py, to enroll the owner's face.

    python enroll_owner.py

Look at the camera. It waits for ~1 second of a single, steady face,
then saves that face's fingerprint to owner_face.npy. Every face the
agent sees later gets compared against this file.
"""
import cv2
import numpy as np

import config
from face_id import detect_faces, get_embedding


def main():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        print("[!] Could not open webcam. Check CAMERA_INDEX in config.py")
        return

    print("[*] Look at the camera. Hold still — enrolling...")

    stable_frames = 0
    embedding = None

    while stable_frames < 30:  # roughly one second at ~30 fps
        ok, frame = cap.read()
        if not ok:
            continue

        faces = detect_faces(frame)
        if len(faces) == 1:
            stable_frames += 1
            embedding = get_embedding(frame, faces[0])
        else:
            stable_frames = 0  # reset if 0 or 2+ faces show up mid-enrollment

        cv2.putText(frame, f"Enrolling: {stable_frames}/30", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Enroll Owner Face (q to cancel)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if embedding is not None:
        np.save("owner_face.npy", embedding)
        print("[OK] Owner face enrolled -> owner_face.npy")
    else:
        print("[!] Enrollment failed — no steady single face detected. Try again.")


if __name__ == "__main__":
    main()
