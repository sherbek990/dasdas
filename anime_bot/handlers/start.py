from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from database.db import get_or_create_user, is_vip as check_vip
from utils.keyboards import main_menu
from utils.subscription import subscription_required

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await get_or_create_user(user.id, user.username or "", user.full_name or "")

    vip_status = await check_vip(user.id)

    await message.answer(
        f"👋 Xush kelibsiz, <b>{user.first_name}</b>!\n\n"
        f"🎬 Bu botda siz o'zbek va xorijiy anime seriyalarini tomosha qilishingiz mumkin.\n\n"
        f"{'💎 Siz VIP foydalanuvchisiz!' if vip_status else '🔓 Barcha imkoniyatlardan foydalanish uchun VIP oling.'}\n\n"
        f"📌 Qidirish usullari:\n"
        f"• Nom bo'yicha: 🔍 Qidirish\n"
        f"• Kod bo'yicha: 🎬 Kod orqali\n"
        f"• Janr bo'yicha: 🏷️ Janr {'✅' if vip_status else '🔒 VIP'}\n"
        f"• Yangilar: 🆕 Yangilar {'✅' if vip_status else '🔒 VIP'}\n"
        f"• Toplar: 🔥 Top {'✅' if vip_status else '🔒 VIP'}",
        parse_mode="HTML",
        reply_markup=main_menu(vip_status)
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Yordam</b>\n\n"
        "🔍 <b>Qidirish</b> — anime nomini yozing\n"
        "🎬 <b>Kod orqali</b> — anime kodini kiriting (masalan: NRTO)\n"
        "🏷️ <b>Janr</b> — janr bo'yicha qidirish (VIP)\n"
        "🆕 <b>Yangilar</b> — oxirgi qo'shilgan animalar (VIP)\n"
        "🔥 <b>Top</b> — eng ko'p ko'rilgan animalar (VIP)\n"
        "💎 <b>VIP</b> — premium imkoniyatlar\n"
        "💰 <b>Hisobim</b> — balans va VIP holati\n\n"
        "❓ Muammo yuzaga kelsa admin bilan bog'laning",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "check_sub")
async def check_subscription_callback(callback: CallbackQuery):
    ok, kb = await subscription_required(callback.bot, callback.from_user.id)
    if ok:
        vip_status = await check_vip(callback.from_user.id)
        await callback.message.edit_text(
            "✅ Obuna tasdiqlandi! Endi botdan foydalanishingiz mumkin.\n\n"
            "Menyu uchun /start ni bosing.",
            parse_mode="HTML"
        )
        await callback.message.answer("👇 Menyu:", reply_markup=main_menu(vip_status))
    else:
        await callback.answer("❌ Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
