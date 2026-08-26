"""
SQLite-backed user store for Sanadi AI accounts.

This is a genuinely small, file-based database -- appropriate for a
phase-1 pilot with a handful of users, not a production-scale user base.
If Sanadi AI grows past that, this is the seam to swap for a real hosted
database (Postgres, etc.) without changing the auth logic that calls
these functions.
"""

import sqlite3
import time
import uuid
from pathlib import Path
from typing import Optional

DB_PATH = Path("data/sanadi.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_user(name: str, email: str, password_hash: str) -> dict:
    user_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (id, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email.lower(), password_hash, time.time()),
        )
        conn.commit()
    finally:
        conn.close()
    return {"id": user_id, "name": name, "email": email.lower()}


def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None
