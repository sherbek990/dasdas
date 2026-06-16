from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_user, create_payment, is_vip
from utils.keyboards import vip_keyboard
from config import VIP_PRICE, PAYMENT_CARD, PAYMENT_NAME, PAYMENT_ADMIN, ADMIN_IDS

router = Router()


class VIPState(StatesGroup):
    waiting_screenshot = State()


@router.message(F.text.in_(["💎 VIP olish", "💎 VIP"]))
async def vip_menu(message: Message):
    vip_status = await is_vip(message.from_user.id)
    if vip_status:
        user = await get_user(message.from_user.id)
        expires = user.get("vip_expires", "")
        await message.answer(
            f"💎 <b>Siz allaqachon VIP foydalanuvchisiz!</b>\n\n"
            f"⏰ Muddati tugashi: <b>{expires[:10] if expires else 'Cheksiz'}</b>\n\n"
            f"✅ VIP imkoniyatlar:\n"
            f"• Janr bo'yicha qidirish\n"
            f"• Yangi animalarni ko'rish\n"
            f"• Top animalar\n"
            f"• Reklamasiz tomosha\n"
            f"• Majburiy obunasiz kirish",
            parse_mode="HTML"
        )
        return

    await message.answer(
        f"💎 <b>VIP obuna</b>\n\n"
        f"💰 Narxi: <b>{VIP_PRICE:,} so'm / 30 kun</b>\n\n"
        f"✅ VIP imkoniyatlar:\n"
        f"• 🏷️ Janr bo'yicha qidirish\n"
        f"• 🆕 Yangi animalar\n"
        f"• 🔥 Top animalar\n"
        f"• 📢 Reklamasiz tomosha\n"
        f"• ✅ Majburiy obunasiz kirish\n\n"
        f"VIP sotib olish uchun tugmani bosing 👇",
        parse_mode="HTML",
        reply_markup=vip_keyboard()
    )


@router.callback_query(F.data == "vip_info")
async def vip_info(callback: CallbackQuery):
    await callback.answer(
        "💎 VIP — bu premium obuna bo'lib, barcha imkoniyatlarni ochadi!",
        show_alert=True
    )


@router.callback_query(F.data == "buy_vip")
async def buy_vip(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VIPState.waiting_screenshot)
    await callback.message.answer(
        f"💳 <b>To'lov qilish</b>\n\n"
        f"Quyidagi karta raqamiga <b>{VIP_PRICE:,} so'm</b> o'tkazing:\n\n"
        f"🏦 Karta: <code>{PAYMENT_CARD}</code>\n"
        f"👤 Egasi: <b>{PAYMENT_NAME}</b>\n\n"
        f"✅ To'lov qilgandan so'ng <b>chek (screenshot)</b> yuboring.\n"
        f"⏱️ Admin 24 soat ichida VIP ni faollashtiradi.",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(VIPState.waiting_screenshot, F.photo)
async def receive_vip_screenshot(message: Message, state: FSMContext):
    await state.clear()
    file_id = message.photo[-1].file_id
    user = message.from_user

    payment_id = await create_payment(
        user_id=user.id,
        amount=VIP_PRICE,
        payment_type="vip",
        screenshot_file_id=file_id
    )

    await message.answer(
        f"✅ <b>Chek qabul qilindi!</b>\n\n"
        f"📋 Ariza raqami: <b>#{payment_id}</b>\n"
        f"⏱️ Admin ko'rib chiqadi va VIP faollashtiriladi.\n\n"
        f"❓ Muammo bo'lsa: {PAYMENT_ADMIN}",
        parse_mode="HTML"
    )

    # Adminga xabar yuborish
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_ok:{payment_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay_no:{payment_id}")
    ]])

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=(
                    f"💎 <b>VIP so'rovi #{payment_id}</b>\n\n"
                    f"👤 Foydalanuvchi: {user.full_name}\n"
                    f"🔗 Username: @{user.username or 'yo\'q'}\n"
                    f"🆔 ID: <code>{user.id}</code>\n"
                    f"💰 Summa: {VIP_PRICE:,} so'm"
                ),
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass


@router.message(VIPState.waiting_screenshot)
async def invalid_screenshot(message: Message):
    await message.answer("❗ Iltimos, to'lov cheki rasmini (screenshot) yuboring.")
