import sqlite3
from datetime import datetime

DB_NAME = "yohan_bot.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            registered INTEGER DEFAULT 0,
            one_win_user_id TEXT,
            deposit_amount REAL DEFAULT 0,
            deposit_verified INTEGER DEFAULT 0,
            signals_unlocked INTEGER DEFAULT 0,
            notifications INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    ).fetchone()

    conn.close()
    return user


def create_user(telegram_id, username=None, first_name=None):
    now = datetime.utcnow().isoformat()

    conn = get_connection()

    conn.execute("""
        INSERT OR IGNORE INTO users (
            telegram_id,
            username,
            first_name,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        telegram_id,
        username,
        first_name,
        now,
        now
    ))

    conn.commit()
    conn.close()


def update_user(telegram_id, **fields):
    if not fields:
        return

    fields["updated_at"] = datetime.utcnow().isoformat()

    allowed = {
        "username",
        "first_name",
        "registered",
        "one_win_user_id",
        "deposit_amount",
        "deposit_verified",
        "signals_unlocked",
        "notifications",
        "updated_at",
    }

    fields = {
        key: value
        for key, value in fields.items()
        if key in allowed
    }

    if not fields:
        return

    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values())
    values.append(telegram_id)

    conn = get_connection()

    conn.execute(
        f"""
        UPDATE users
        SET {columns}
        WHERE telegram_id = ?
        """,
        values
    )

    conn.commit()
    conn.close()


def set_deposit(telegram_id, amount, verified=False):
    amount = float(amount)

    unlocked = (
        verified
        and amount >= 25.00
    )

    update_user(
        telegram_id,
        deposit_amount=amount,
        deposit_verified=int(verified),
        signals_unlocked=int(unlocked)
    )


def can_access_signals(telegram_id):
    user = get_user(telegram_id)

    if not user:
        return False

    return (
        bool(user["registered"])
        and bool(user["deposit_verified"])
        and float(user["deposit_amount"] or 0) >= 25.00
        and bool(user["signals_unlocked"])
    )
