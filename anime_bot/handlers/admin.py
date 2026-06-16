from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_stats, confirm_payment, reject_payment, get_user,
    add_anime, update_anime, delete_anime, get_anime_by_code,
    add_episode, delete_episode, set_vip, get_pending_payments
)
from utils.keyboards import main_menu
from config import ADMIN_IDS

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ─── FILTER ──────────────────────────────────────────────────────

from aiogram.filters import BaseFilter
from aiogram.types import Message

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return is_admin(message.from_user.id)


# ─── HOLATLAR ────────────────────────────────────────────────────

class AddAnimeState(StatesGroup):
    waiting_data = State()


class AddEpisodeState(StatesGroup):
    waiting_anime_code = State()
    waiting_episode_num = State()
    waiting_video = State()


class BroadcastState(StatesGroup):
    waiting_message = State()


# ─── ADMIN PANEL ─────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats = await get_stats()
    await message.answer(
        f"⚙️ <b>Admin Panel</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"💎 VIP: <b>{stats['vip_users']}</b>\n"
        f"🎬 Animalar: <b>{stats['anime_count']}</b>\n"
        f"📺 Epizodlar: <b>{stats['episode_count']}</b>\n\n"
        f"📋 <b>Buyruqlar:</b>\n"
        f"/addanime — Anime qo'shish\n"
        f"/addep — Epizod qo'shish\n"
        f"/delanime — Anime o'chirish\n"
        f"/delep — Epizod o'chirish\n"
        f"/setvip — VIP berish\n"
        f"/payments — Kutayotgan to'lovlar\n"
        f"/broadcast — Hammaga xabar\n"
        f"/stats — Statistika",
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats = await get_stats()
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        f"💎 VIP foydalanuvchilar: {stats['vip_users']}\n"
        f"🎬 Animalar soni: {stats['anime_count']}\n"
        f"📺 Jami epizodlar: {stats['episode_count']}",
        parse_mode="HTML"
    )


# ─── ANIME QO'SHISH ───────────────────────────────────────────────

@router.message(Command("addanime"))
async def add_anime_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddAnimeState.waiting_data)
    await message.answer(
        "🎬 <b>Anime qo'shish</b>\n\n"
        "Quyidagi formatda yuboring:\n\n"
        "<code>"
        "Kod: NRTO\n"
        "Nomi (UZ): Naruto\n"
        "Nomi (EN): Naruto\n"
        "Nomi (RU): Наруто\n"
        "Janr: Aksyon, Fantastika\n"
        "Yil: 2002\n"
        "Mamlakat: Yaponiya\n"
        "Til: O'zbekcha\n"
        "Tavsif: Bu yerga qisqacha tavsif yozing"
        "</code>",
        parse_mode="HTML"
    )


@router.message(AddAnimeState.waiting_data)
async def process_add_anime(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    lines = message.text.strip().split("\n")
    data = {}
    for line in lines:
        if ":" in line:
            key, _, value = line.partition(":")
            data[key.strip().lower()] = value.strip()

    anime_data = {
        "code": data.get("kod", "").upper(),
        "name_uz": data.get("nomi (uz)", data.get("nomi", "")),
        "name_en": data.get("nomi (en)", ""),
        "name_ru": data.get("nomi (ru)", ""),
        "genre": data.get("janr", ""),
        "year": int(data.get("yil", 0)) if data.get("yil", "").isdigit() else None,
        "country": data.get("mamlakat", ""),
        "language": data.get("til", ""),
        "description": data.get("tavsif", ""),
        "poster_file_id": None,
        "total_episodes": 0
    }

    if not anime_data["code"] or not anime_data["name_uz"]:
        await message.answer("❗ Kod va nom majburiy! Qayta urinib ko'ring.")
        await state.clear()
        return

    try:
        await add_anime(anime_data)
        await state.clear()
        await message.answer(
            f"✅ <b>{anime_data['name_uz']}</b> muvaffaqiyatli qo'shildi!\n"
            f"🔑 Kod: <code>{anime_data['code']}</code>\n\n"
            f"Epizod qo'shish uchun: /addep",
            parse_mode="HTML"
        )
    except Exception as e:
        await state.clear()
        await message.answer(f"❌ Xato: {e}\n\nBu kod allaqachon mavjud bo'lishi mumkin.")


# ─── EPIZOD QO'SHISH ─────────────────────────────────────────────

@router.message(Command("addep"))
async def add_episode_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddEpisodeState.waiting_anime_code)
    await message.answer("📺 Anime kodini kiriting (masalan: <code>NRTO</code>):", parse_mode="HTML")


@router.message(AddEpisodeState.waiting_anime_code)
async def process_ep_code(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    anime = await get_anime_by_code(code)
    if not anime:
        await message.answer(f"❌ <code>{code}</code> kodi topilmadi. Qayta kiriting:", parse_mode="HTML")
        return
    await state.update_data(anime_code=code)
    await state.set_state(AddEpisodeState.waiting_episode_num)
    await message.answer(
        f"✅ Anime: <b>{anime['name_uz']}</b>\n\n"
        f"Epizod raqamini kiriting (masalan: 1):",
        parse_mode="HTML"
    )


@router.message(AddEpisodeState.waiting_episode_num)
async def process_ep_num(message: Message, state: FSMContext):
    try:
        ep_num = int(message.text.strip())
    except ValueError:
        await message.answer("❗ Faqat raqam kiriting!")
        return
    await state.update_data(episode_number=ep_num)
    await state.set_state(AddEpisodeState.waiting_video)
    await message.answer(f"🎥 {ep_num}-epizod videosini yuboring:")


@router.message(AddEpisodeState.waiting_video, F.video)
async def process_ep_video(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    file_id = message.video.file_id
    await add_episode(
        anime_code=data["anime_code"],
        episode_number=data["episode_number"],
        video_file_id=file_id
    )
    await message.answer(
        f"✅ {data['episode_number']}-epizod qo'shildi!\n"
        f"Anime: <code>{data['anime_code']}</code>\n\n"
        f"Keyingi epizod uchun /addep",
        parse_mode="HTML"
    )


@router.message(AddEpisodeState.waiting_video)
async def invalid_video(message: Message):
    await message.answer("❗ Iltimos, video fayl yuboring.")


# ─── O'CHIRISH ───────────────────────────────────────────────────

@router.message(Command("delanime"))
async def del_anime(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: /delanime KOD\nMasalan: /delanime NRTO")
        return
    code = args[1].upper()
    await delete_anime(code)
    await message.answer(f"✅ <code>{code}</code> o'chirildi.", parse_mode="HTML")


@router.message(Command("delep"))
async def del_episode(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Foydalanish: /delep KOD EPIZOD_RAQAMI\nMasalan: /delep NRTO 5")
        return
    code = args[1].upper()
    try:
        ep_num = int(args[2])
    except ValueError:
        await message.answer("❗ Epizod raqami butun son bo'lishi kerak!")
        return
    await delete_episode(code, ep_num)
    await message.answer(f"✅ <code>{code}</code> {ep_num}-epizod o'chirildi.", parse_mode="HTML")


# ─── VIP BERISH ──────────────────────────────────────────────────

@router.message(Command("setvip"))
async def set_vip_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: /setvip USER_ID [kunlar]\nMasalan: /setvip 123456789 30")
        return
    try:
        user_id = int(args[1])
        days = int(args[2]) if len(args) > 2 else 30
    except ValueError:
        await message.answer("❗ Noto'g'ri format!")
        return

    await set_vip(user_id, days)
    await message.answer(f"✅ {user_id} ga {days} kunlik VIP berildi!")
    try:
        await message.bot.send_message(
            user_id,
            f"🎉 <b>VIP faollashtirildi!</b>\n\n"
            f"💎 Siz endi <b>{days} kun</b> davomida VIP foydalanuvchisiz!\n"
            f"Barcha imkoniyatlar ochildi. /start bosing.",
            parse_mode="HTML"
        )
    except Exception:
        pass


# ─── TO'LOVLARNI TASDIQLASH ──────────────────────────────────────

@router.message(Command("payments"))
async def pending_payments(message: Message):
    if not is_admin(message.from_user.id):
        return
    payments = await get_pending_payments()
    if not payments:
        await message.answer("✅ Kutayotgan to'lovlar yo'q.")
        return
    await message.answer(f"💳 Kutayotgan to'lovlar: <b>{len(payments)}</b> ta\n\nHar bir to'lov uchun tugmalar yuborilgan xabarlarda.", parse_mode="HTML")


@router.callback_query(F.data.startswith("pay_ok:"))
async def confirm_payment_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[1])
    payment = await confirm_payment(payment_id)

    if not payment:
        await callback.answer("❌ To'lov topilmadi yoki allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    await callback.message.edit_caption(
        callback.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Tasdiqlandi!")

    try:
        if payment["payment_type"] == "vip":
            text = "🎉 <b>VIP obunangiz faollashtirildi!</b>\n\n💎 30 kunlik VIP obuna. /start bosing."
        else:
            text = f"✅ <b>{payment['amount']:,.0f} so'm</b> balansingizga qo'shildi!"
        await callback.bot.send_message(payment["user_id"], text, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data.startswith("pay_no:"))
async def reject_payment_cb(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[1])
    payment_data = await reject_payment(payment_id, "Admin rad etdi")

    await callback.message.edit_caption(
        callback.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
        parse_mode="HTML"
    )
    await callback.answer("❌ Rad etildi!")


# ─── BROADCAST ───────────────────────────────────────────────────

@router.message(Command("broadcast"))
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(BroadcastState.waiting_message)
    await message.answer("📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n/cancel — bekor qilish")


@router.message(BroadcastState.waiting_message)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    await state.clear()
    from database.db import get_all_users
    users = await get_all_users()

    sent = 0
    failed = 0
    for user_id in users:
        try:
            await message.forward(user_id)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"📢 Xabar yuborildi!\n"
        f"✅ Muvaffaqiyatli: {sent}\n"
        f"❌ Xato: {failed}"
    )


@router.message(Command("cancel"))
async def cancel_state(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu(False))
