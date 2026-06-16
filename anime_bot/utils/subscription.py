from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import REQUIRED_CHANNELS
from database.db import is_vip


async def check_subscription(bot: Bot, user_id: int) -> list:
    """Foydalanuvchi obuna bo'lmagan kanallar ro'yxatini qaytaradi"""
    not_subscribed = []
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel["channel_id"], user_id)
            if member.status in ("left", "kicked", "banned"):
                not_subscribed.append(channel)
        except Exception:
            not_subscribed.append(channel)
    return not_subscribed


def subscription_keyboard(not_subscribed: list) -> InlineKeyboardMarkup:
    """Obuna bo'lish uchun tugmalar"""
    buttons = []
    for ch in not_subscribed:
        buttons.append([InlineKeyboardButton(
            text=f"📢 {ch['name']}",
            url=ch["invite_link"]
        )])
    buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def subscription_required(bot: Bot, user_id: int) -> tuple[bool, InlineKeyboardMarkup | None]:
    """
    VIP bo'lsa yoki barcha kanallarga obuna bo'lsa True qaytaradi.
    Aks holda False va tugmalar qaytaradi.
    """
    if await is_vip(user_id):
        return True, None

    not_subscribed = await check_subscription(bot, user_id)
    if not_subscribed:
        kb = subscription_keyboard(not_subscribed)
        return False, kb
    return True, None
