import aiosqlite
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)


async def init_db():
    """Ma'lumotlar bazasini yaratish va jadvallarni sozlash"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                is_vip INTEGER DEFAULT 0,
                vip_expires TEXT,
                balance REAL DEFAULT 0.0,
                joined_at TEXT DEFAULT (datetime('now')),
                last_active TEXT DEFAULT (datetime('now'))
            )
        """)

        # Anime jadvali (admin qo'lda qo'shadi)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name_uz TEXT NOT NULL,
                name_en TEXT,
                name_ru TEXT,
                genre TEXT,
                year INTEGER,
                country TEXT,
                language TEXT,
                total_episodes INTEGER DEFAULT 0,
                description TEXT,
                poster_file_id TEXT,
                is_active INTEGER DEFAULT 1,
                views INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Epizodlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_code TEXT NOT NULL,
                episode_number INTEGER NOT NULL,
                title TEXT,
                video_file_id TEXT NOT NULL,
                duration INTEGER,
                views INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (anime_code) REFERENCES anime(code),
                UNIQUE(anime_code, episode_number)
            )
        """)

        # To'lovlar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                screenshot_file_id TEXT,
                admin_note TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                confirmed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Statistika
        await db.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                anime_code TEXT,
                episode_number INTEGER,
                action TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        await db.commit()
    logger.info("✅ Ma'lumotlar bazasi tayyor")


# ─── FOYDALANUVCHI ───────────────────────────────────────────────

async def get_or_create_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name,
                last_active = datetime('now')
        """, (user_id, username, full_name))
        await db.commit()
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return dict(await cur.fetchone())


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def is_vip(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT is_vip, vip_expires FROM users WHERE user_id = ?
        """, (user_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return False
            is_vip_status, expires = row
            if not is_vip_status:
                return False
            if expires:
                from datetime import datetime
                if datetime.fromisoformat(expires) < datetime.now():
                    await db.execute("UPDATE users SET is_vip = 0 WHERE user_id = ?", (user_id,))
                    await db.commit()
                    return False
            return True


async def set_vip(user_id: int, days: int = 30):
    from datetime import datetime, timedelta
    expires = (datetime.now() + timedelta(days=days)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET is_vip = 1, vip_expires = ? WHERE user_id = ?
        """, (expires, user_id))
        await db.commit()


async def get_balance(user_id: int) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0.0


async def update_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1") as cur:
            vip_count = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM anime WHERE is_active = 1") as cur:
            anime_count = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM episodes") as cur:
            ep_count = (await cur.fetchone())[0]
        return {"total_users": total, "vip_users": vip_count, "anime_count": anime_count, "episode_count": ep_count}


# ─── ANIME ──────────────────────────────────────────────────────

async def add_anime(data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO anime (code, name_uz, name_en, name_ru, genre, year, country, language, total_episodes, description, poster_file_id)
            VALUES (:code, :name_uz, :name_en, :name_ru, :genre, :year, :country, :language, :total_episodes, :description, :poster_file_id)
        """, data)
        await db.commit()


async def get_anime_by_code(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM anime WHERE code = ? AND is_active = 1", (code.upper(),)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def search_anime_by_name(query: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM anime WHERE is_active = 1 AND (
                name_uz LIKE ? OR name_en LIKE ? OR name_ru LIKE ?
            ) LIMIT 10
        """, (f"%{query}%", f"%{query}%", f"%{query}%")) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def search_anime_by_genre(genre: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM anime WHERE is_active = 1 AND genre LIKE ? LIMIT 20
        """, (f"%{genre}%",)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def get_latest_anime(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM anime WHERE is_active = 1 ORDER BY created_at DESC LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def get_top_viewed_anime(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM anime WHERE is_active = 1 ORDER BY views DESC LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def increment_anime_views(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE anime SET views = views + 1 WHERE code = ?", (code,))
        await db.commit()


async def update_anime(code: str, data: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        sets = ", ".join(f"{k} = ?" for k in data)
        values = list(data.values()) + [code.upper()]
        await db.execute(f"UPDATE anime SET {sets} WHERE code = ?", values)
        await db.commit()


async def delete_anime(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE anime SET is_active = 0 WHERE code = ?", (code.upper(),))
        await db.commit()


# ─── EPIZODLAR ──────────────────────────────────────────────────

async def add_episode(anime_code: str, episode_number: int, video_file_id: str, title: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO episodes (anime_code, episode_number, video_file_id, title)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(anime_code, episode_number) DO UPDATE SET
                video_file_id = excluded.video_file_id,
                title = excluded.title
        """, (anime_code.upper(), episode_number, video_file_id, title))
        # Umumiy epizod sonini yangilash
        await db.execute("""
            UPDATE anime SET total_episodes = (
                SELECT COUNT(*) FROM episodes WHERE anime_code = ?
            ) WHERE code = ?
        """, (anime_code.upper(), anime_code.upper()))
        await db.commit()


async def get_episode(anime_code: str, episode_number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM episodes WHERE anime_code = ? AND episode_number = ?
        """, (anime_code.upper(), episode_number)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_episodes_list(anime_code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT episode_number FROM episodes WHERE anime_code = ? ORDER BY episode_number
        """, (anime_code.upper(),)) as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]


async def delete_episode(anime_code: str, episode_number: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM episodes WHERE anime_code = ? AND episode_number = ?
        """, (anime_code.upper(), episode_number))
        await db.execute("""
            UPDATE anime SET total_episodes = (
                SELECT COUNT(*) FROM episodes WHERE anime_code = ?
            ) WHERE code = ?
        """, (anime_code.upper(), anime_code.upper()))
        await db.commit()


# ─── TO'LOVLAR ──────────────────────────────────────────────────

async def create_payment(user_id: int, amount: float, payment_type: str, screenshot_file_id: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            INSERT INTO payments (user_id, amount, payment_type, screenshot_file_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, amount, payment_type, screenshot_file_id)) as cur:
            return cur.lastrowid


async def get_pending_payments():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT p.*, u.full_name, u.username
            FROM payments p JOIN users u ON p.user_id = u.user_id
            WHERE p.status = 'pending' ORDER BY p.created_at
        """) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def confirm_payment(payment_id: int, admin_note: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)) as cur:
            payment = await cur.fetchone()
        if not payment:
            return None
        payment = dict(payment)

        await db.execute("""
            UPDATE payments SET status = 'confirmed', admin_note = ?, confirmed_at = datetime('now')
            WHERE id = ?
        """, (admin_note, payment_id))

        if payment["payment_type"] == "vip":
            await db.execute("UPDATE users SET is_vip = 1, vip_expires = datetime('now', '+30 days') WHERE user_id = ?",
                             (payment["user_id"],))
        else:
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",
                             (payment["amount"], payment["user_id"]))

        await db.commit()
        return payment


async def reject_payment(payment_id: int, reason: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE payments SET status = 'rejected', admin_note = ? WHERE id = ?
        """, (reason, payment_id))
        await db.commit()
