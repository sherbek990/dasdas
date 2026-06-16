from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database import get_all_sponsors


async def check_user_subscriptions(bot: Bot, user_id: int) -> list:
    """
    Foydalanuvchi barcha homiy kanallarga obuna bo'lganini tekshiradi.
    Qaytaradi: obuna bo'lmagan kanallar ro'yxati
    """
    sponsors = get_all_sponsors()
    not_subscribed = []

    for sponsor in sponsors:
        try:
            member = await bot.get_chat_member(
                chat_id=sponsor["channel_id"],
                user_id=user_id
            )
            if member.status in ("left", "kicked", "banned"):
                not_subscribed.append(dict(sponsor))
        except (TelegramForbiddenError, TelegramBadRequest):
            # Bot kanalda admin emas yoki kanal topilmadi - o'tkazib yuboramiz
            pass
        except Exception:
            pass

    return not_subscribed


def build_subscribe_keyboard(not_subscribed: list, anime_id: int) -> InlineKeyboardMarkup:
    """Obuna bo'lmagan kanallar uchun tugmalar"""
    buttons = []

    for ch in not_subscribed:
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {ch['channel_name']}",
                url=ch["channel_link"]
            )
        ])

    # Tekshirish tugmasi
    buttons.append([
        InlineKeyboardButton(
            text="✅ Obunani tekshirish",
            callback_data=f"check_sub:{anime_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
