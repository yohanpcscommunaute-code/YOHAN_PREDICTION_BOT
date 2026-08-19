import sqlite3
from datetime import datetime


DB_NAME = "yohan_bot.db"
MIN_DEPOSIT = 25.00


# ============================================================
# CONNEXION
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# INITIALISATION
# ============================================================

def init_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,

            language TEXT DEFAULT 'fr',

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


# Compatibilité avec l'ancien nom
def init_db():
    init_database()


# ============================================================
# UTILISATEUR
# ============================================================

def get_user(telegram_id):
    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE telegram_id = ?
        """,
        (telegram_id,)
    ).fetchone()

    conn.close()

    return user


def register_user(user):
    now = datetime.utcnow().isoformat()

    conn = get_connection()

    existing = conn.execute(
        """
        SELECT id
        FROM users
        WHERE telegram_id = ?
        """,
        (user.id,)
    ).fetchone()

    if existing:

        conn.execute(
            """
            UPDATE users
            SET username = ?,
                first_name = ?,
                updated_at = ?
            WHERE telegram_id = ?
            """,
            (
                user.username,
                user.first_name,
                now,
                user.id
            )
        )

    else:

        conn.execute(
            """
            INSERT INTO users (
                telegram_id,
                username,
                first_name,
                language,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user.id,
                user.username,
                user.first_name,
                "fr",
                now,
                now
            )
        )

    conn.commit()
    conn.close()


# Compatibilité avec l'ancien système
def create_user(
    telegram_id,
    username=None,
    first_name=None
):

    now = datetime.utcnow().isoformat()

    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO users (
            telegram_id,
            username,
            first_name,
            language,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            username,
            first_name,
            "fr",
            now,
            now
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# MISE À JOUR
# ============================================================

def update_user(telegram_id, **fields):

    if not fields:
        return

    allowed = {
        "username",
        "first_name",
        "language",
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

    fields["updated_at"] = datetime.utcnow().isoformat()

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


# ============================================================
# LANGUE
# ============================================================

def get_language(telegram_id):

    user = get_user(telegram_id)

    if not user:
        return "fr"

    return user["language"] or "fr"


def set_language(
    telegram_id,
    language
):

    allowed_languages = {
        "fr",
        "en",
        "es",
        "la",
        "ar",
        "pt",
        "zh",
        "hi",
        "ru",
    }

    if language not in allowed_languages:
        language = "fr"

    update_user(
        telegram_id,
        language=language
    )


# ============================================================
# INSCRIPTION
# ============================================================

def set_registration_verified(
    telegram_id,
    verified=True,
    one_win_user_id=None
):

    fields = {
        "registered": int(bool(verified))
    }

    if one_win_user_id is not None:
        fields["one_win_user_id"] = str(
            one_win_user_id
        )

    update_user(
        telegram_id,
        **fields
    )

    refresh_signal_access(
        telegram_id
    )


def is_registration_verified(
    telegram_id
):

    user = get_user(telegram_id)

    if not user:
        return False

    return bool(
        user["registered"]
    )


# ============================================================
# DÉPÔT
# ============================================================

def set_deposit(
    telegram_id,
    amount,
    verified=False
):

    amount = float(amount)

    update_user(
        telegram_id,
        deposit_amount=amount,
        deposit_verified=int(
            bool(verified)
        )
    )

    refresh_signal_access(
        telegram_id
    )


def is_deposit_verified(
    telegram_id
):

    user = get_user(telegram_id)

    if not user:
        return False

    return bool(
        user["deposit_verified"]
    )


# ============================================================
# ACCÈS AUX SIGNAUX
# ============================================================

def refresh_signal_access(
    telegram_id
):

    user = get_user(telegram_id)

    if not user:
        return False

    unlocked = (
        bool(user["registered"])
        and bool(user["deposit_verified"])
        and float(
            user["deposit_amount"] or 0
        ) >= MIN_DEPOSIT
    )

    update_user(
        telegram_id,
        signals_unlocked=int(unlocked)
    )

    return unlocked


def is_user_fully_verified(
    telegram_id
):

    user = get_user(telegram_id)

    if not user:
        return False

    unlocked = (
        bool(user["registered"])
        and bool(user["deposit_verified"])
        and float(
            user["deposit_amount"] or 0
        ) >= MIN_DEPOSIT
    )

    # On resynchronise toujours le statut.
    if bool(user["signals_unlocked"]) != unlocked:

        update_user(
            telegram_id,
            signals_unlocked=int(unlocked)
        )

    return unlocked


def can_access_signals(
    telegram_id
):

    return is_user_fully_verified(
        telegram_id
    )
