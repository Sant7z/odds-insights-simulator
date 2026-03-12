import sqlite3
from pathlib import Path

DB_PATH = Path("data/simulations.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            sport TEXT NOT NULL,
            requested_events INTEGER NOT NULL,
            combined_odds REAL NOT NULL,
            stake REAL NOT NULL,
            hypothetical_return REAL NOT NULL,
            events_json TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()