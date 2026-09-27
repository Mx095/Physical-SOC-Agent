"""
Central configuration for the Physical SOC Agent.
Edit these values to match your machine and MySQL setup.
"""

# --- Camera ---
CAMERA_INDEX = 0             # 0 = default webcam
SHOW_PREVIEW_WINDOW = True   # set False to run fully headless in the terminal

# --- Detection thresholds ---
NO_FACE_LOCK_SECONDS = 5      # how long you can be out of frame before the PC locks
SECOND_FACE_COOLDOWN = 10     # seconds between repeated "second face" alerts (avoid spam)

# --- MySQL ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_DB_password",   # <-- change this
    "database": "physical_soc",
}

# --- Storage ---
SNAPSHOT_DIR = "snapshots"

# --- API ---
API_HOST = "127.0.0.1"
API_PORT = 8000
