import sqlite3
from datetime import datetime, timedelta

DATABASE = "yohan_prediction.db"


def get_db():
    return sqlite3.connect(DATABASE)


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


def get_language(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT language FROM users WHERE id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result[0] if result else "fr"


def set_language(user_id, language):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET language = ?
        WHERE id = ?
    """, (language, user_id))

    conn.commit()
    conn.close()


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
    """, (now, user_id))

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
        SELECT COUNT(*)
        FROM predictions
        WHERE game = 'luckyjet'
    """)
    lucky = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM predictions
        WHERE game = 'rocketqueen'
    """)
    rocket = cursor.fetchone()[0]

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
        "lucky": lucky,
        "rocket": rocket,
        "fr": languages.get("fr", 0),
        "en": languages.get("en", 0)
  }
