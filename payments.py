from datetime import datetime

from config import PAYMENT_MIN_AMOUNT
from database import get_connection


def create_deposit(
    telegram_id,
    amount,
    method,
    reference
):
    amount = float(amount)

    if amount < PAYMENT_MIN_AMOUNT:
        return False

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            method TEXT NOT NULL,
            reference TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            verified_at TEXT
        )
        """
    )

    conn.execute(
        """
        INSERT INTO deposits (
            telegram_id,
            amount,
            method,
            reference,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, 'PENDING', ?)
        """,
        (
            telegram_id,
            amount,
            method,
            reference,
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()

    return True


def get_pending_deposit(telegram_id):
    conn = get_connection()

    deposit = conn.execute(
        """
        SELECT *
        FROM deposits
        WHERE telegram_id = ?
        AND status = 'PENDING'
        ORDER BY id DESC
        LIMIT 1
        """,
        (telegram_id,)
    ).fetchone()

    conn.close()

    return deposit
