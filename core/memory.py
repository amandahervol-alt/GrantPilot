# Storage: SQLite via Python's built-in sqlite3 module.
# Reasoning: Org data is structured (mission, programs, stats) and benefits from
# relational storage. SQLite requires zero setup, persists across sessions, and
# handles CRUD cleanly. No external dependencies needed for this scope.

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "grantpilot.db"


def _get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS org_profile (
                id     INTEGER PRIMARY KEY CHECK (id = 1),
                mission         TEXT DEFAULT '',
                geographic_reach TEXT DEFAULT '',
                history         TEXT DEFAULT '',
                leadership      TEXT DEFAULT '',
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS programs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT DEFAULT '',
                outcomes    TEXT DEFAULT '',
                population  TEXT DEFAULT '',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                value TEXT NOT NULL
            )
        """)
        conn.commit()


# --- Org Profile ---

def get_org_profile() -> dict:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM org_profile WHERE id = 1").fetchone()
        return dict(row) if row else {}


def save_org_profile(data: dict):
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO org_profile (id, mission, geographic_reach, history, leadership)
            VALUES (1, :mission, :geographic_reach, :history, :leadership)
            ON CONFLICT(id) DO UPDATE SET
                mission          = excluded.mission,
                geographic_reach = excluded.geographic_reach,
                history          = excluded.history,
                leadership       = excluded.leadership,
                updated_at       = CURRENT_TIMESTAMP
        """, data)
        conn.commit()


# --- Programs ---

def get_programs() -> list:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM programs ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def add_program(data: dict) -> int:
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO programs (name, description, outcomes, population) "
            "VALUES (:name, :description, :outcomes, :population)",
            data,
        )
        conn.commit()
        return cur.lastrowid


def update_program(program_id: int, data: dict):
    with _get_conn() as conn:
        conn.execute(
            "UPDATE programs SET name=:name, description=:description, "
            "outcomes=:outcomes, population=:population WHERE id=:id",
            {**data, "id": program_id},
        )
        conn.commit()


def delete_program(program_id: int):
    with _get_conn() as conn:
        conn.execute("DELETE FROM programs WHERE id=?", (program_id,))
        conn.commit()


# --- Stats ---

def get_stats() -> list:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM stats ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def save_stats(stats_list: list):
    with _get_conn() as conn:
        conn.execute("DELETE FROM stats")
        if stats_list:
            conn.executemany(
                "INSERT INTO stats (label, value) VALUES (:label, :value)",
                stats_list,
            )
        conn.commit()


# --- Combined ---

def get_all_memory() -> dict:
    return {
        "profile": get_org_profile(),
        "programs": get_programs(),
        "stats": get_stats(),
    }
