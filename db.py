"""
Thin MySQL data-access layer.
Every write from the agent, and every read for the API, goes through here —
this is what makes the API and the agent independent processes that both
mirror your SSH monitoring architecture (agent writes, API only reads).
"""
import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def insert_event(event_type: str, severity: str, description: str, snapshot_path: str = None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (event_type, severity, description, snapshot_path) "
        "VALUES (%s, %s, %s, %s)",
        (event_type, severity, description, snapshot_path),
    )
    conn.commit()
    cur.close()
    conn.close()


def fetch_events(limit: int = 50):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def fetch_alerts(limit: int = 50):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM events WHERE severity IN ('warning','critical') "
        "ORDER BY created_at DESC LIMIT %s",
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def fetch_summary():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT event_type, severity, COUNT(*) AS count FROM events "
        "GROUP BY event_type, severity"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
