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
            created_at TEXT
        )
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
# UTILISATEURS
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
                created_at
            )
            VALUES (?, ?, ?, 'fr', 0, ?, ?)
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
# LANGUE
# ============================================================

def get_language(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT language FROM users WHERE id = ?",
        (user_id,)
    )

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

    # Nombre total d'utilisateurs
    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    users = cursor.fetchone()[0]

    # Utilisateurs actifs durant les dernières 24 heures
    limit = (
        datetime.now() - timedelta(hours=24)
    ).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE last_activity >= ?
    """, (
        limit,
    ))

    active = cursor.fetchone()[0]

    # Nombre total de prédictions
    cursor.execute(
        "SELECT COUNT(*) FROM predictions"
    )

    predictions = cursor.fetchone()[0]

    # Statistiques par jeu
    cursor.execute("""
        SELECT game, COUNT(*)
        FROM predictions
        GROUP BY game
    """)

    games = dict(cursor.fetchall())

    # Statistiques par langue
    cursor.execute("""
        SELECT language, COUNT(*)
        FROM users
        GROUP BY language
    """)

    languages = dict(cursor.fetchall())

    conn.close()

    return {
        "users": users,
        "active": active,
        "predictions": predictions,
        "games": games,
        "languages": languages,
        }
