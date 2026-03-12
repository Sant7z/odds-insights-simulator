import json
from datetime import datetime
from app.db.connection import get_connection


def save_simulation(sport: str, requested_events: int, combined_odds: float, stake: float, hypothetical_return: float, events: list):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO simulations (
            created_at, sport, requested_events, combined_odds, stake, hypothetical_return, events_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        sport,
        requested_events,
        combined_odds,
        stake,
        hypothetical_return,
        json.dumps(events, ensure_ascii=False),
    ))

    conn.commit()
    conn.close()


def list_simulations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM simulations
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]