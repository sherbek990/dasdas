import sqlite3
from config import DB_FILE


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Barcha jadvallarni yaratish"""
    conn = get_conn()
    cur = conn.cursor()

    # Adminlar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Homiy kanallar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sponsor_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE NOT NULL,
            channel_name TEXT,
            channel_link TEXT,
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Animlar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS animes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            file_id TEXT NOT NULL,
            file_type TEXT DEFAULT 'video',
            episode INTEGER DEFAULT 1,
            season INTEGER DEFAULT 1,
            thumbnail_id TEXT,
            post_message_id INTEGER,
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Foydalanuvchilar jadvali (statistika uchun)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Ma'lumotlar bazasi tayyor!")


# ─── ADMINLAR ───────────────────────────────────────────

def add_admin(telegram_id: int, username: str, added_by: int) -> bool:
    try:
        conn = get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO admins (telegram_id, username, added_by) VALUES (?, ?, ?)",
            (telegram_id, username, added_by)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def remove_admin(telegram_id: int) -> bool:
    conn = get_conn()
    cur = conn.execute("DELETE FROM admins WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def get_all_admins():
    conn = get_conn()
    admins = conn.execute("SELECT * FROM admins").fetchall()
    conn.close()
    return admins


def is_admin(telegram_id: int) -> bool:
    conn = get_conn()
    result = conn.execute(
        "SELECT id FROM admins WHERE telegram_id = ?", (telegram_id,)
    ).fetchone()
    conn.close()
    return result is not None


# ─── HOMIY KANALLAR ─────────────────────────────────────

def add_sponsor(channel_id: str, channel_name: str, channel_link: str, added_by: int) -> bool:
    try:
        conn = get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO sponsor_channels (channel_id, channel_name, channel_link, added_by) VALUES (?, ?, ?, ?)",
            (channel_id, channel_name, channel_link, added_by)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def remove_sponsor(channel_id: str) -> bool:
    conn = get_conn()
    cur = conn.execute("DELETE FROM sponsor_channels WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def get_all_sponsors():
    conn = get_conn()
    sponsors = conn.execute("SELECT * FROM sponsor_channels").fetchall()
    conn.close()
    return sponsors


# ─── ANIMLAR ────────────────────────────────────────────

def add_anime(title: str, description: str, file_id: str, file_type: str,
              episode: int, season: int, thumbnail_id: str, added_by: int) -> int:
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO animes (title, description, file_id, file_type, episode, season, thumbnail_id, added_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, description, file_id, file_type, episode, season, thumbnail_id, added_by)
    )
    anime_id = cur.lastrowid
    conn.commit()
    conn.close()
    return anime_id


def update_anime_post_id(anime_id: int, post_message_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE animes SET post_message_id = ? WHERE id = ?",
        (post_message_id, anime_id)
    )
    conn.commit()
    conn.close()


def get_anime(anime_id: int):
    conn = get_conn()
    anime = conn.execute("SELECT * FROM animes WHERE id = ?", (anime_id,)).fetchone()
    conn.close()
    return anime


def get_all_animes():
    conn = get_conn()
    animes = conn.execute("SELECT * FROM animes ORDER BY added_at DESC").fetchall()
    conn.close()
    return animes


def delete_anime(anime_id: int) -> bool:
    conn = get_conn()
    cur = conn.execute("DELETE FROM animes WHERE id = ?", (anime_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


# ─── FOYDALANUVCHILAR ───────────────────────────────────

def register_user(telegram_id: int, username: str, full_name: str):
    conn = get_conn()
    conn.execute(
        """INSERT OR IGNORE INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)""",
        (telegram_id, username, full_name)
    )
    conn.execute(
        "UPDATE users SET last_active = CURRENT_TIMESTAMP, username = ?, full_name = ? WHERE telegram_id = ?",
        (username, full_name, telegram_id)
    )
    conn.commit()
    conn.close()


def get_user_count() -> int:
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count
