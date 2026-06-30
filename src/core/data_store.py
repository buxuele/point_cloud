"""
Data Store.
Manages:
  - Audit log (SQLite): every bypass / baseline / setting change event
  - Bypass history for chart queries
  - CSV export
  - Point cloud snapshot saves (as .npy files, 6-month retention)
"""
from __future__ import annotations

import csv
import os
import sqlite3
import time
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np

# Adjust DATA_DIR to be one level up since this file is in src/core/ and data is in src/data/
DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "audit.db")
SNAPSHOT_DIR = os.path.join(DATA_DIR, "snapshots")


class DataStore:

    def __init__(self, db_path: str = DB_PATH):
        dir_name = os.path.dirname(db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        self._db_path = db_path
        self._init_db()
        self._seed_demo_history()
        self._cleanup_old_snapshots()
        self._cleanup_old_audit_logs()

    # Audit Log

    def log_event(self, elevator_id: str, action: str,
                  occupancy_pct: float, result: str):
        """
        Actions: 'BYPASS_SENT' | 'SET_BASELINE' | 'CLEAR_BASELINE'
                 | 'CHANGE_CAPACITY' | 'APP_CLOSED'
        """
        ts = datetime.utcnow().isoformat()
        self._execute(
            "INSERT INTO audit_log (timestamp, elevator_id, action, occupancy_pct, result)"
            " VALUES (?,?,?,?,?)",
            (ts, elevator_id, action, round(occupancy_pct, 2), result)
        )

    def get_bypass_events(
        self, elevator_id: str, hours: int = 24
    ) -> List[dict]:
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        rows = self._fetchall(
            "SELECT timestamp, occupancy_pct FROM audit_log"
            " WHERE elevator_id=? AND action='BYPASS_SENT' AND timestamp>=?"
            " ORDER BY timestamp",
            (elevator_id, since)
        )
        return [{"timestamp": r[0], "occupancy_pct": r[1]} for r in rows]

    def get_bypass_count(self, elevator_id: str, hours: int = 24) -> int:
        since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        row = self._fetchone(
            "SELECT COUNT(*) FROM audit_log"
            " WHERE elevator_id=? AND action='BYPASS_SENT' AND timestamp>=?",
            (elevator_id, since)
        )
        return row[0] if row else 0

    def export_csv(self, path: str, elevator_id: Optional[str] = None):
        if elevator_id:
            rows = self._fetchall(
                "SELECT * FROM audit_log WHERE elevator_id=? ORDER BY timestamp",
                (elevator_id,)
            )
        else:
            rows = self._fetchall(
                "SELECT * FROM audit_log ORDER BY timestamp", ()
            )
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "elevator_id", "action",
                              "occupancy_pct", "result"])
            writer.writerows(rows)

    # Point Cloud Snapshots

    def save_snapshot(self, elevator_id: str, cloud: np.ndarray):
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_id = elevator_id.replace(" ", "_")
        filename = f"{safe_id}_{ts}.npy"
        path = os.path.join(SNAPSHOT_DIR, filename)
        np.save(path, cloud)
        return path

    def _cleanup_old_snapshots(self, months: int = 6):
        """Delete snapshot files older than `months` months."""
        cutoff = time.time() - months * 30 * 86400
        for fname in os.listdir(SNAPSHOT_DIR):
            fpath = os.path.join(SNAPSHOT_DIR, fname)
            if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff:
                os.remove(fpath)

    def _cleanup_old_audit_logs(self, years: int = 5):
        """Delete audit logs older than `years` years."""
        cutoff_date = (datetime.utcnow() - timedelta(days=years*365)).isoformat()
        self._execute("DELETE FROM audit_log WHERE timestamp < ?", (cutoff_date,))

    def clear_all_data(self):
        """Clear all audit logs and snapshot files."""
        self._execute("DELETE FROM audit_log")
        for fname in os.listdir(SNAPSHOT_DIR):
            fpath = os.path.join(SNAPSHOT_DIR, fname)
            if os.path.isfile(fpath):
                try:
                    os.remove(fpath)
                except Exception as e:
                    print(f"[WARN] Failed to delete snapshot {fpath}: {e}")

    # Internal DB helpers

    def _init_db(self):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp     TEXT NOT NULL,
                    elevator_id   TEXT NOT NULL,
                    action        TEXT NOT NULL,
                    occupancy_pct REAL,
                    result        TEXT
                )
            """)
            conn.commit()

    def _seed_demo_history(self):
        """Seed fake bypass events over the last 7 days so the chart looks good."""
        row = self._fetchone("SELECT COUNT(*) FROM audit_log WHERE action='BYPASS_SENT'")
        if row and row[0] > 0:
            return  # Already has data

        import random
        elevators = ["Elevator 1", "Elevator 2", "Elevator 3", "Elevator 4", "Elevator 5"]
        now = datetime.utcnow()

        events = []
        for _ in range(300):
            days_ago = random.uniform(0, 7)
            ts = (now - timedelta(days=days_ago)).isoformat()
            eid = random.choice(elevators)
            occ = random.uniform(85.0, 100.0)
            events.append((ts, eid, 'BYPASS_SENT', occ, 'OK'))

        # Sort by timestamp
        events.sort(key=lambda x: x[0])

        with sqlite3.connect(self._db_path) as conn:
            conn.executemany(
                "INSERT INTO audit_log (timestamp, elevator_id, action, occupancy_pct, result) VALUES (?,?,?,?,?)",
                events
            )
            conn.commit()

    def _execute(self, sql: str, params=()):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(sql, params)
            conn.commit()

    def _fetchone(self, sql: str, params=()):
        with sqlite3.connect(self._db_path) as conn:
            return conn.execute(sql, params).fetchone()

    def _fetchall(self, sql: str, params=()):
        with sqlite3.connect(self._db_path) as conn:
            return conn.execute(sql, params).fetchall()
