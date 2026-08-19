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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            provider TEXT DEFAULT 'mixx',
            transaction_id TEXT UNIQUE,
            status TEXT DEFAULT 'PENDING',
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


def create_user(
    telegram_id,
    username=None,
    first_name=None
):
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

    columns = ", ".join(
        f"{key} = ?"
        for key in fields
    )

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


def create_deposit(
    telegram_id,
    amount,
    transaction_id=None
):
    now = datetime.utcnow().isoformat()

    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO deposits (
            telegram_id,
            amount,
            provider,
            transaction_id,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, 'mixx', ?, 'PENDING', ?, ?)
    """, (
        telegram_id,
        float(amount),
        transaction_id,
        now,
        now
    ))

    deposit_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return deposit_id


def get_deposit(deposit_id):

    conn = get_connection()

    deposit = conn.execute(
        "SELECT * FROM deposits WHERE id = ?",
        (deposit_id,)
    ).fetchone()

    conn.close()

    return deposit


def verify_deposit(
    deposit_id,
    transaction_id=None
):
    now = datetime.utcnow().isoformat()

    conn = get_connection()

    deposit = conn.execute(
        "SELECT * FROM deposits WHERE id = ?",
        (deposit_id,)
    ).fetchone()

    if not deposit:
        conn.close()
        return False

    if float(deposit["amount"]) < 5000:
        conn.close()
        return False

    conn.execute("""
        UPDATE deposits
        SET status = 'COMPLETED',
            transaction_id = COALESCE(?, transaction_id),
            updated_at = ?
        WHERE id = ?
    """, (
        transaction_id,
        now,
        deposit_id
    ))

    conn.execute("""
        UPDATE users
        SET deposit_amount = ?,
            deposit_verified = 1,
            signals_unlocked = 1,
            updated_at = ?
        WHERE telegram_id = ?
    """, (
        float(deposit["amount"]),
        now,
        deposit["telegram_id"]
    ))

    conn.commit()
    conn.close()

    return True


def fail_deposit(deposit_id):

    now = datetime.utcnow().isoformat()

    conn = get_connection()

    conn.execute("""
        UPDATE deposits
        SET status = 'FAILED',
            updated_at = ?
        WHERE id = ?
    """, (
        now,
        deposit_id
    ))

    conn.commit()
    conn.close()


def can_access_signals(telegram_id):

    user = get_user(telegram_id)

    if not user:
        return False

    return (
        bool(user["registered"])
        and bool(user["deposit_verified"])
        and float(user["deposit_amount"] or 0) >= 5000
        and bool(user["signals_unlocked"])
        )
def get_language(telegram_id):
    user = get_user(telegram_id)

    if not user:
        return "fr"

    try:
        return user["language"] or "fr"
    except (KeyError, IndexError):
        return "fr"


def set_language(telegram_id, language):
    allowed = {
        "fr",
        "en",
        "es",
        "pt",
        "ru",
        "ar",
        "zh",
        "hi",
        "la",
    }

    if language not in allowed:
        language = "fr"

    update_user(
        telegram_id,
        language=language
        )
