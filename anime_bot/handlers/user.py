from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from database import get_anime, get_all_sponsors
from utils import check_user_subscriptions, build_subscribe_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    """Start komandasi - faqat salomlashish"""
    await message.answer(
        "🎌 <b>Anime Bot ga xush kelibsiz!</b>\n\n"
        "📺 Yangi animlarni ko'rish uchun kanalimizni kuzating!\n"
        "▶️ Anime postidagi <b>«Tomosha qilish»</b> tugmasini bosing.",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("watch:"))
async def watch_anime(callback: CallbackQuery, bot: Bot):
    """
    Kanal postidagi 'Tomosha qilish' tugmasi bosilganda ishga tushadi.
    Foydalanuvchini botga yo'naltiradi va obunani tekshiradi.
    """
    anime_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    await callback.answer("⏳ Tekshirilmoqda...")

    # Obunani tekshirish
    not_subscribed = await check_user_subscriptions(bot, user_id)

    if not_subscribed:
        # Obuna bo'lmagan kanallar bor
        text = (
            "⚠️ <b>Animeni ko'rish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
        )
        for i, ch in enumerate(not_subscribed, 1):
            text += f"{i}. 📢 {ch['channel_name']}\n"

        text += "\nObuna bo'lgandan so'ng ✅ <b>«Obunani tekshirish»</b> tugmasini bosing."

        keyboard = build_subscribe_keyboard(not_subscribed, anime_id)

        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        # Barcha kanallarga obuna - animeni yuborish
        await send_anime_to_user(callback.message, bot, anime_id)


@router.callback_query(F.data.startswith("check_sub:"))
async def check_subscription(callback: CallbackQuery, bot: Bot):
    """Obunani qayta tekshirish tugmasi"""
    anime_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    await callback.answer("⏳ Obuna tekshirilmoqda...")

    not_subscribed = await check_user_subscriptions(bot, user_id)

    if not_subscribed:
        text = (
            "❌ <b>Siz hali quyidagi kanallarga obuna bo'lmadingiz:</b>\n\n"
        )
        for i, ch in enumerate(not_subscribed, 1):
            text += f"{i}. 📢 {ch['channel_name']}\n"

        text += "\nObuna bo'lib ✅ <b>«Obunani tekshirish»</b> tugmasini qayta bosing."

        keyboard = build_subscribe_keyboard(not_subscribed, anime_id)
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        # Obuna tasdiqlandi - animeni yuborish
        await callback.message.delete()
        await send_anime_to_user(callback.message, bot, anime_id)


async def send_anime_to_user(message: Message, bot: Bot, anime_id: int):
    """Foydalanuvchiga anime faylini yuborish"""
    anime = get_anime(anime_id)

    if not anime:
        await message.answer("❌ Anime topilmadi yoki o'chirilgan.")
        return

    caption = (
        f"🎌 <b>{anime['title']}</b>\n"
        f"📺 Mavsum: {anime['season']} | Qism: {anime['episode']}\n\n"
        f"📝 {anime['description'] or ''}\n\n"
        f"<i>🎬 Tomosha qiling!</i>"
    )

    try:
        if anime["file_type"] == "video":
            await bot.send_video(
                chat_id=message.chat.id,
                video=anime["file_id"],
                caption=caption,
                parse_mode="HTML"
            )
        elif anime["file_type"] == "document":
            await bot.send_document(
                chat_id=message.chat.id,
                document=anime["file_id"],
                caption=caption,
                parse_mode="HTML"
            )
        elif anime["file_type"] == "photo":
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=anime["file_id"],
                caption=caption,
                parse_mode="HTML"
            )
    except Exception as e:
        await message.answer(f"❌ Anime yuborishda xatolik: {e}")
