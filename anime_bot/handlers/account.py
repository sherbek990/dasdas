from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import get_user, get_balance, create_payment, is_vip
from config import PAYMENT_CARD, PAYMENT_NAME, PAYMENT_ADMIN, ADMIN_IDS

router = Router()

DEPOSIT_AMOUNTS = [10000, 20000, 50000, 100000]


class DepositState(StatesGroup):
    waiting_amount = State()
    waiting_screenshot = State()


@router.message(F.text == "💰 Hisobim")
async def my_account(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Iltimos /start bosing")
        return

    vip_status = await is_vip(message.from_user.id)
    balance = user.get("balance", 0)
    expires = user.get("vip_expires", "")

    text = (
        f"💰 <b>Mening hisobim</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism: {user.get('full_name', '—')}\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"💵 Balans: <b>{balance:,.0f} so'm</b>\n"
        f"💎 VIP: {'✅ Faol' if vip_status else '❌ Faol emas'}\n"
    )
    if vip_status and expires:
        text += f"⏰ VIP tugashi: <b>{expires[:10]}</b>\n"

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "➕ Pul kiritish")
async def deposit_start(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10,000 so'm", callback_data="deposit:10000"),
            InlineKeyboardButton(text="20,000 so'm", callback_data="deposit:20000"),
        ],
        [
            InlineKeyboardButton(text="50,000 so'm", callback_data="deposit:50000"),
            InlineKeyboardButton(text="100,000 so'm", callback_data="deposit:100000"),
        ],
        [InlineKeyboardButton(text="✏️ Boshqa miqdor", callback_data="deposit:custom")]
    ])
    await message.answer(
        "➕ <b>Pul kiritish</b>\n\nQancha miqdor kiritmoqchisiz?",
        parse_mode="HTML",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("deposit:"))
async def deposit_amount(callback: CallbackQuery, state: FSMContext):
    amount_str = callback.data.split(":")[1]

    if amount_str == "custom":
        await state.set_state(DepositState.waiting_amount)
        await callback.message.answer("✏️ Miqdorni kiriting (so'mda, masalan: 35000):")
        await callback.answer()
        return

    amount = int(amount_str)
    await state.update_data(amount=amount)
    await state.set_state(DepositState.waiting_screenshot)
    await send_payment_instructions(callback.message, amount)
    await callback.answer()


@router.message(DepositState.waiting_amount)
async def process_custom_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip().replace(" ", "").replace(",", ""))
        if amount < 1000:
            await message.answer("❗ Minimum miqdor 1,000 so'm")
            return
    except ValueError:
        await message.answer("❗ Faqat raqam kiriting (masalan: 25000)")
        return

    await state.update_data(amount=amount)
    await state.set_state(DepositState.waiting_screenshot)
    await send_payment_instructions(message, amount)


async def send_payment_instructions(message: Message, amount: int):
    await message.answer(
        f"💳 <b>To'lov qilish</b>\n\n"
        f"Quyidagi karta raqamiga <b>{amount:,} so'm</b> o'tkazing:\n\n"
        f"🏦 Karta: <code>{PAYMENT_CARD}</code>\n"
        f"👤 Egasi: <b>{PAYMENT_NAME}</b>\n\n"
        f"✅ To'lov qilgandan so'ng <b>chek (screenshot)</b> yuboring.",
        parse_mode="HTML"
    )


@router.message(DepositState.waiting_screenshot, F.photo)
async def receive_deposit_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount", 0)
    await state.clear()

    file_id = message.photo[-1].file_id
    user = message.from_user

    payment_id = await create_payment(
        user_id=user.id,
        amount=amount,
        payment_type="deposit",
        screenshot_file_id=file_id
    )

    await message.answer(
        f"✅ <b>Chek qabul qilindi!</b>\n\n"
        f"📋 Ariza: <b>#{payment_id}</b>\n"
        f"💰 Miqdor: <b>{amount:,} so'm</b>\n"
        f"⏱️ Admin tasdiqlashi keyin balansingizga qo'shiladi.\n\n"
        f"❓ Muammo: {PAYMENT_ADMIN}",
        parse_mode="HTML"
    )

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
                    f"💰 <b>Depozit so'rovi #{payment_id}</b>\n\n"
                    f"👤 {user.full_name} | @{user.username or 'yo\'q'}\n"
                    f"🆔 <code>{user.id}</code>\n"
                    f"💵 Miqdor: {amount:,} so'm"
                ),
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass


@router.message(DepositState.waiting_screenshot)
async def invalid_deposit_screenshot(message: Message):
    await message.answer("❗ Iltimos, to'lov cheki rasmini (screenshot) yuboring.")
