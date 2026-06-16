from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import SUPERADMIN_ID
from database import add_admin, remove_admin, get_all_admins, is_admin, get_user_count

router = Router()


def is_superadmin(user_id: int) -> bool:
    return user_id == SUPERADMIN_ID


class AddAdminState(StatesGroup):
    waiting_id = State()


class RemoveAdminState(StatesGroup):
    waiting_id = State()


# ─── SuperAdmin Panel ─────────────────────────────────────

@router.message(Command("superadmin"))
async def superadmin_panel(message: Message):
    if not is_superadmin(message.from_user.id):
        return

    count = get_user_count()
    admins = get_all_admins()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Admin qo'shish", callback_data="sa:add_admin"),
            InlineKeyboardButton(text="🗑 Admin o'chirish", callback_data="sa:remove_admin"),
        ],
        [
            InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data="sa:list_admins"),
        ],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="sa:stats"),
        ]
    ])

    await message.answer(
        f"👑 <b>SuperAdmin Panel</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{count}</b>\n"
        f"🛠 Adminlar soni: <b>{len(admins)}</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ─── Admin qo'shish ──────────────────────────────────────

@router.callback_query(F.data == "sa:add_admin")
async def start_add_admin(callback: CallbackQuery, state: FSMContext):
    if not is_superadmin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "👤 <b>Admin qo'shish</b>\n\n"
        "Yangi admin Telegram ID sini yuboring:\n\n"
        "<i>💡 ID ni bilish uchun @userinfobot ga /start yozing</i>",
        parse_mode="HTML"
    )
    await state.set_state(AddAdminState.waiting_id)
    await callback.answer()


@router.message(AddAdminState.waiting_id)
async def add_admin_handler(message: Message, state: FSMContext, bot: Bot):
    if not is_superadmin(message.from_user.id):
        return

    try:
        new_admin_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting (Telegram ID)!")
        return

    # Foydalanuvchi ma'lumotlarini olish
    try:
        user_info = await bot.get_chat(new_admin_id)
        username = user_info.username or user_info.full_name or str(new_admin_id)
    except Exception:
        username = str(new_admin_id)

    success = add_admin(
        telegram_id=new_admin_id,
        username=username,
        added_by=message.from_user.id
    )

    if success:
        await message.answer(
            f"✅ <b>Admin qo'shildi!</b>\n\n"
            f"👤 Foydalanuvchi: {username}\n"
            f"🆔 ID: <code>{new_admin_id}</code>",
            parse_mode="HTML"
        )
        # Yangi adminga xabar yuborish
        try:
            await bot.send_message(
                new_admin_id,
                "🎉 Siz admin qildingiz! /admin yozing."
            )
        except Exception:
            pass
    else:
        await message.answer("⚠️ Bu foydalanuvchi allaqachon admin!")

    await state.clear()


# ─── Admin o'chirish ─────────────────────────────────────

@router.callback_query(F.data == "sa:remove_admin")
async def remove_admin_menu(callback: CallbackQuery):
    if not is_superadmin(callback.from_user.id):
        return

    admins = get_all_admins()
    if not admins:
        await callback.message.edit_text("📭 Admin yo'q.")
        await callback.answer()
        return

    buttons = []
    for a in admins:
        buttons.append([
            InlineKeyboardButton(
                text=f"🗑 {a['username'] or a['telegram_id']}",
                callback_data=f"sa_del_admin:{a['telegram_id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="sa:back")])

    await callback.message.edit_text(
        "🗑 <b>O'chirmoqchi bo'lgan adminni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sa_del_admin:"))
async def delete_admin_handler(callback: CallbackQuery, bot: Bot):
    if not is_superadmin(callback.from_user.id):
        return

    admin_id = int(callback.data.split(":")[1])
    success = remove_admin(admin_id)

    if success:
        await callback.message.edit_text(
            f"✅ Admin o'chirildi: <code>{admin_id}</code>", parse_mode="HTML"
        )
        try:
            await bot.send_message(admin_id, "⚠️ Sizning admin huquqingiz olib qolindi.")
        except Exception:
            pass
    else:
        await callback.message.edit_text("❌ Admin topilmadi.")
    await callback.answer()


# ─── Adminlar ro'yxati ───────────────────────────────────

@router.callback_query(F.data == "sa:list_admins")
async def list_admins(callback: CallbackQuery):
    if not is_superadmin(callback.from_user.id):
        return

    admins = get_all_admins()
    if not admins:
        await callback.message.edit_text("📭 Hali admin qo'shilmagan.")
        await callback.answer()
        return

    text = "📋 <b>Adminlar ro'yxati:</b>\n\n"
    for i, a in enumerate(admins, 1):
        text += f"{i}. {a['username'] or 'Noma\'lum'} — <code>{a['telegram_id']}</code>\n"

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


# ─── Statistika ──────────────────────────────────────────

@router.callback_query(F.data == "sa:stats")
async def stats(callback: CallbackQuery):
    if not is_superadmin(callback.from_user.id):
        return

    from database import get_all_animes, get_all_sponsors
    users = get_user_count()
    animes = len(get_all_animes())
    sponsors = len(get_all_sponsors())
    admins = len(get_all_admins())

    text = (
        f"📊 <b>Bot statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"🎌 Animlar: <b>{animes}</b>\n"
        f"📢 Homiy kanallar: <b>{sponsors}</b>\n"
        f"🛠 Adminlar: <b>{admins}</b>"
    )

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "sa:back")
async def sa_back(callback: CallbackQuery):
    await superadmin_panel(callback.message)
    await callback.answer()
