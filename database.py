import sqlite3
from datetime import datetime, timedelta

DATABASE = "yohan_prediction.db"


# ============================================================
# CONNEXION
# ============================================================

def get_db():
    return sqlite3.connect(DATABASE)


# ============================================================
# INITIALISATION
# ============================================================

def init_database():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            language TEXT DEFAULT 'fr',
            predictions INTEGER DEFAULT 0,
            last_activity TEXT,
            created_at TEXT,
            registration_verified INTEGER DEFAULT 0,
            deposit_verified INTEGER DEFAULT 0
        )
    """)

    # Migration des anciennes bases
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    if "registration_verified" not in columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN registration_verified INTEGER DEFAULT 0
        """)

    if "deposit_verified" not in columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN deposit_verified INTEGER DEFAULT 0
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game TEXT,
            odds REAL,
            safe REAL,
            signal_time TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# UTILISATEUR
# ============================================================

def register_user(user):

    conn = get_db()
    cursor = conn.cursor()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute(
        "SELECT id FROM users WHERE id = ?",
        (user.id,)
    )

    exists = cursor.fetchone()

    if exists:

        cursor.execute("""
            UPDATE users
            SET name = ?,
                username = ?,
                last_activity = ?
            WHERE id = ?
        """, (
            user.first_name,
            user.username or "",
            now,
            user.id
        ))

    else:

        cursor.execute("""
            INSERT INTO users (
                id,
                name,
                username,
                language,
                predictions,
                last_activity,
                created_at,
                registration_verified,
                deposit_verified
            )
            VALUES (?, ?, ?, 'fr', 0, ?, ?, 0, 0)
        """, (
            user.id,
            user.first_name,
            user.username or "",
            now,
            now
        ))

    conn.commit()
    conn.close()


# ============================================================
# STATUT INSCRIPTION
# ============================================================

def is_registration_verified(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT registration_verified
        FROM users
        WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return bool(result and result[0])


def set_registration_verified(
    user_id,
    verified=True
):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET registration_verified = ?
        WHERE id = ?
    """, (
        1 if verified else 0,
        user_id
    ))

    conn.commit()
    conn.close()


# ============================================================
# STATUT DÉPÔT
# ============================================================

def is_deposit_verified(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT deposit_verified
        FROM users
        WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return bool(result and result[0])


def set_deposit_verified(
    user_id,
    verified=True
):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET deposit_verified = ?
        WHERE id = ?
    """, (
        1 if verified else 0,
        user_id
    ))

    conn.commit()
    conn.close()


# ============================================================
# VÉRIFICATION COMPLÈTE
# ============================================================

def is_user_fully_verified(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            registration_verified,
            deposit_verified
        FROM users
        WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    if not result:
        return False

    registration_verified = bool(result[0])
    deposit_verified = bool(result[1])

    return (
        registration_verified
        and
        deposit_verified
    )


# ============================================================
# LANGUE
# ============================================================

def get_language(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT language
        FROM users
        WHERE id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    if result and result[0]:
        return result[0]

    return "fr"


def set_language(user_id, language):

    allowed_languages = [
        "fr",
        "en",
        "es",
        "la",
        "ar",
        "pt",
        "zh",
        "hi",
        "ru",
    ]

    if language not in allowed_languages:
        return False

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET language = ?
        WHERE id = ?
    """, (
        language,
        user_id
    ))

    conn.commit()
    conn.close()

    return True


# ============================================================
# ACTIVITÉ
# ============================================================

def update_activity(user_id):

    conn = get_db()
    cursor = conn.cursor()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE users
        SET last_activity = ?
        WHERE id = ?
    """, (
        now,
        user_id
    ))

    conn.commit()
    conn.close()


# ============================================================
# PRÉDICTIONS
# ============================================================

def save_prediction(
    user_id,
    game,
    odds,
    safe,
    signal_time
):

    conn = get_db()
    cursor = conn.cursor()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE users
        SET predictions = predictions + 1,
            last_activity = ?
        WHERE id = ?
    """, (
        now,
        user_id
    ))

    cursor.execute("""
        INSERT INTO predictions (
            user_id,
            game,
            odds,
            safe,
            signal_time,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        game,
        odds,
        safe,
        signal_time,
        now
    ))

    conn.commit()
    conn.close()


# ============================================================
# STATISTIQUES
# ============================================================

def get_statistics():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    users = cursor.fetchone()[0]

    limit = (
        datetime.now() - timedelta(hours=24)
    ).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE last_activity >= ?
    """, (limit,))

    active = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM predictions"
    )

    predictions = cursor.fetchone()[0]

    cursor.execute("""
        SELECT game, COUNT(*)
        FROM predictions
        GROUP BY game
    """)

    games = dict(cursor.fetchall())

    cursor.execute("""
        SELECT language, COUNT(*)
        FROM users
        GROUP BY language
    """)

    languages = dict(cursor.fetchall())

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE registration_verified = 1
    """)

    verified_registrations = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE deposit_verified = 1
    """)

    verified_deposits = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE registration_verified = 1
          AND deposit_verified = 1
    """)

    fully_verified = cursor.fetchone()[0]

    conn.close()

    return {
        "users": users,
        "active": active,
        "predictions": predictions,
        "games": games,
        "languages": languages,
        "verified_registrations": verified_registrations,
        "verified_deposits": verified_deposits,
        "fully_verified": fully_verified,
    }
