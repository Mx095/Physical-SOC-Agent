"""
Face recognition engine.

face_utils.py (Haar Cascade) only ever COUNTED faces. This module
IDENTIFIES them, using two small neural nets that ship as part of
OpenCV's core `objdetect` module (no extra libraries needed):

  1. YuNet (FaceDetectorYN)   -> finds faces AND 5 landmarks per face
  2. SFace (FaceRecognizerSF) -> turns an aligned face into a 128-D
                                  numeric "fingerprint" (embedding)

Two different people's fingerprints are far apart in that 128-D space;
the same person's fingerprint, even in a different photo, lands close
together. That distance IS how Face ID (and this module) recognizes
someone: enroll once, then compare every new face's fingerprint to the
one you saved.
"""
import os
import cv2

_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
_DETECTOR_PATH = os.path.join(_MODELS_DIR, "face_detection_yunet_2023mar.onnx")
_RECOGNIZER_PATH = os.path.join(_MODELS_DIR, "face_recognition_sface_2021dec.onnx")

# SFace's own published cutoff: cosine similarity >= this -> same person.
# (Published by the OpenCV Zoo alongside the model itself.)
MATCH_THRESHOLD = 0.363

_detector = cv2.FaceDetectorYN.create(_DETECTOR_PATH, "", (320, 320), score_threshold=0.7)
_recognizer = cv2.FaceRecognizerSF.create(_RECOGNIZER_PATH, "")


def detect_faces(frame):
    """Returns a list of face rows: [x, y, w, h, 5x(landmark x,y), score]."""
    h, w = frame.shape[:2]
    _detector.setInputSize((w, h))
    _, faces = _detector.detect(frame)
    return faces if faces is not None else []


def get_embedding(frame, face):
    """Turns one detected face into its 128-D fingerprint."""
    aligned = _recognizer.alignCrop(frame, face)
    return _recognizer.feature(aligned)


def is_owner(embedding, owner_embedding) -> bool:
    """Compares a fingerprint to the enrolled owner's fingerprint."""
    score = _recognizer.match(embedding, owner_embedding, cv2.FaceRecognizerSF_FR_COSINE)
    return score >= MATCH_THRESHOLD


def draw_faces(frame, faces, labels=None):
    labels = labels or [None] * len(faces)
    for face, label in zip(faces, labels):
        x, y, w, h = face[:4].astype(int)
        color = (0, 255, 0) if label == "OWNER" else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        if label:
            cv2.putText(frame, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame
