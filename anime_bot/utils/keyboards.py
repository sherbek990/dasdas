from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import EPISODES_PER_PAGE


def main_menu(is_vip: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu"""
    buttons = [
        [KeyboardButton(text="🔍 Qidirish"), KeyboardButton(text="🎬 Kod orqali")],
    ]
    if is_vip:
        buttons.append([KeyboardButton(text="🏷️ Janr"), KeyboardButton(text="🆕 Yangilar")])
        buttons.append([KeyboardButton(text="🔥 Top"), KeyboardButton(text="💎 VIP")])
    else:
        buttons.append([KeyboardButton(text="🏷️ Janr 🔒"), KeyboardButton(text="🆕 Yangilar 🔒")])
        buttons.append([KeyboardButton(text="🔥 Top 🔒"), KeyboardButton(text="💎 VIP olish")])
    buttons.append([KeyboardButton(text="💰 Hisobim"), KeyboardButton(text="➕ Pul kiritish")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def anime_info_keyboard(anime_code: str, total_episodes: int) -> InlineKeyboardMarkup:
    """Anime ma'lumotlari ostidagi tugmalar"""
    buttons = []
    if total_episodes > 0:
        buttons.append([InlineKeyboardButton(
            text=f"▶️ Epizodlarni ko'rish ({total_episodes} ta)",
            callback_data=f"episodes:{anime_code}:1"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def episodes_keyboard(anime_code: str, episode_numbers: list, page: int = 1) -> InlineKeyboardMarkup:
    """Epizodlar sahifalangan klaviaturasi"""
    total = len(episode_numbers)
    total_pages = (total + EPISODES_PER_PAGE - 1) // EPISODES_PER_PAGE

    start = (page - 1) * EPISODES_PER_PAGE
    end = start + EPISODES_PER_PAGE
    current_episodes = episode_numbers[start:end]

    buttons = []
    row = []
    for i, ep_num in enumerate(current_episodes):
        row.append(InlineKeyboardButton(
            text=f"▶️ {ep_num}",
            callback_data=f"watch:{anime_code}:{ep_num}"
        ))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Navigatsiya tugmalari
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"episodes:{anime_code}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="ignore"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"episodes:{anime_code}:{page + 1}"))
    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def anime_list_keyboard(anime_list: list) -> InlineKeyboardMarkup:
    """Anime ro'yxatidan tanlash"""
    buttons = []
    for anime in anime_list:
        name = anime.get("name_uz") or anime.get("name_en", "Nomsiz")
        buttons.append([InlineKeyboardButton(
            text=f"🎬 {name} ({anime.get('year', '?')})",
            callback_data=f"anime:{anime['code']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 VIP sotib olish", callback_data="buy_vip")],
        [InlineKeyboardButton(text="❓ VIP haqida", callback_data="vip_info")]
    ])


def payment_confirm_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_ok:{payment_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay_no:{payment_id}")
        ]
    ])


def format_anime_info(anime: dict) -> str:
    """Anime ma'lumotlarini chiroyli formatda ko'rsatish"""
    name = anime.get("name_uz", "")
    name_en = anime.get("name_en", "")
    name_ru = anime.get("name_ru", "")

    names_line = name
    if name_en:
        names_line += f" / {name_en}"
    if name_ru:
        names_line += f" / {name_ru}"

    text = f"🎬 <b>{names_line}</b>\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"

    if anime.get("code"):
        text += f"🔑 <b>Kod:</b> <code>{anime['code']}</code>\n"
    if anime.get("genre"):
        text += f"🏷️ <b>Janr:</b> {anime['genre']}\n"
    if anime.get("year"):
        text += f"📅 <b>Yil:</b> {anime['year']}\n"
    if anime.get("country"):
        text += f"🌍 <b>Mamlakat:</b> {anime['country']}\n"
    if anime.get("language"):
        text += f"🗣️ <b>Til:</b> {anime['language']}\n"
    if anime.get("total_episodes"):
        text += f"📺 <b>Epizodlar:</b> {anime['total_episodes']} ta\n"
    if anime.get("views"):
        text += f"👁️ <b>Ko'rishlar:</b> {anime['views']}\n"
    if anime.get("description"):
        text += f"\n📝 {anime['description']}\n"

    return text
