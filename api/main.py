"""
Read-only REST API over the `events` MySQL table.

Run with (from the project root):
    uvicorn api.main:app --reload --port 8000

Then open:
    http://127.0.0.1:8000/docs   -> interactive Swagger dashboard
    http://127.0.0.1:8000/events -> raw JSON
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from db import fetch_events, fetch_alerts, fetch_summary

app = FastAPI(title="Physical SOC Agent API")


@app.get("/events")
def get_events(limit: int = 50):
    return fetch_events(limit)


@app.get("/alerts")
def get_alerts(limit: int = 50):
    return fetch_alerts(limit)


@app.get("/summary")
def get_summary():
    return fetch_summary()
