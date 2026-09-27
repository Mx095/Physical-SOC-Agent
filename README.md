# Physical SOC Agent

A terminal-run physical-security agent with real face recognition (not
just face counting): it enrolls YOUR face once, then locks your session
if you leave frame, and logs an alert if anyone else's face appears —
the same core idea Face ID uses.

## Setup

1. `pip install -r requirements.txt`
2. Create the database: `Get-Content schema.sql | mysql -u root -p` (or the cmd/`SOURCE` equivalent).
3. Open `config.py` and set your MySQL password (and camera index, if not 0).
4. Download the two small ONNX models into a `models/` folder:
   ```powershell
   mkdir models -Force
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx" -OutFile "models\face_detection_yunet_2023mar.onnx"
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx" -OutFile "models\face_recognition_sface_2021dec.onnx"
   ```

## Run

**Enroll your face once (only needs to be done once, or again if you delete owner_face.npy):**
```
python enroll_owner.py
```

**Terminal 1 — the agent:**
```
python agent.py
```

**Terminal 2 — the dashboard API (optional, browse logged events):**
```
uvicorn api.main:app --reload --port 8000
```
Then open http://127.0.0.1:8000/docs in a browser. This does NOT start
automatically with the agent — it's a separate process you run whenever
you want to check the logs.

## Why OpenCV is pinned to 4.14.0.94

OpenCV 5.0 (released mid-2026) currently ships pip wheels with an empty
bundled haarcascade data folder (a known, unfixed bug), and moved
CascadeClassifier into a separate contrib package. Since we've dropped
Haar Cascade entirely in favor of YuNet + SFace (which live in OpenCV's
core module in every version), pinning to the last stable 4.x release
sidesteps all of that instability.

## Why no cloud deployment

The agent needs direct access to your laptop's webcam and your OS's
lock command, so it has to run on your machine, not a server. The
FastAPI part only reads the MySQL logs — running both locally is the
correct architecture here, not a limitation.
