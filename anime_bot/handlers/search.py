from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_anime_by_code, search_anime_by_name, search_anime_by_genre,
    get_latest_anime, get_top_viewed_anime, increment_anime_views, is_vip
)
from utils.keyboards import (
    main_menu, anime_info_keyboard, anime_list_keyboard,
    episodes_keyboard, format_anime_info
)
from utils.subscription import subscription_required
from config import AD_TEXT

router = Router()


class SearchState(StatesGroup):
    waiting_name = State()
    waiting_code = State()
    waiting_genre = State()


# ─── TUGMALAR ────────────────────────────────────────────────────

@router.message(F.text == "🔍 Qidirish")
async def search_by_name_start(message: Message, state: FSMContext):
    ok, kb = await subscription_required(message.bot, message.from_user.id)
    if not ok:
        await message.answer("📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=kb)
        return
    await state.set_state(SearchState.waiting_name)
    await message.answer("🔍 Anime nomini yozing (o'zbekcha, inglizcha yoki ruscha):")


@router.message(F.text == "🎬 Kod orqali")
async def search_by_code_start(message: Message, state: FSMContext):
    ok, kb = await subscription_required(message.bot, message.from_user.id)
    if not ok:
        await message.answer("📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=kb)
        return
    await state.set_state(SearchState.waiting_code)
    await message.answer("🎬 Anime kodini kiriting (masalan: <code>NRTO</code>):", parse_mode="HTML")


@router.message(F.text.in_(["🏷️ Janr", "🏷️ Janr 🔒"]))
async def search_by_genre_start(message: Message, state: FSMContext):
    ok, kb = await subscription_required(message.bot, message.from_user.id)
    if not ok:
        await message.answer("📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=kb)
        return
    if not await is_vip(message.from_user.id):
        await message.answer(
            "🔒 Bu funksiya faqat <b>VIP</b> foydalanuvchilar uchun!\n\n"
            "💎 VIP olish uchun <b>VIP olish</b> tugmasini bosing.",
            parse_mode="HTML"
        )
        return
    await state.set_state(SearchState.waiting_genre)
    await message.answer(
        "🏷️ Janrni yozing:\n\n"
        "Masalan: <i>aksyon, komediya, romantika, fantastika, drama, triller, spora, maktab, isekai</i>",
        parse_mode="HTML"
    )


@router.message(F.text.in_(["🆕 Yangilar", "🆕 Yangilar 🔒"]))
async def latest_anime(message: Message):
    ok, kb = await subscription_required(message.bot, message.from_user.id)
    if not ok:
        await message.answer("📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=kb)
        return
    if not await is_vip(message.from_user.id):
        await message.answer(
            "🔒 Bu funksiya faqat <b>VIP</b> foydalanuvchilar uchun!\n\n"
            "💎 VIP olish uchun tugmani bosing.",
            parse_mode="HTML"
        )
        return
    anime_list = await get_latest_anime(10)
    if not anime_list:
        await message.answer("📭 Hozircha anime yo'q.")
        return
    await message.answer(
        "🆕 <b>Oxirgi qo'shilgan animalar:</b>",
        parse_mode="HTML",
        reply_markup=anime_list_keyboard(anime_list)
    )


@router.message(F.text.in_(["🔥 Top", "🔥 Top 🔒"]))
async def top_anime(message: Message):
    ok, kb = await subscription_required(message.bot, message.from_user.id)
    if not ok:
        await message.answer("📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=kb)
        return
    if not await is_vip(message.from_user.id):
        await message.answer(
            "🔒 Bu funksiya faqat <b>VIP</b> foydalanuvchilar uchun!\n\n"
            "💎 VIP olish uchun tugmani bosing.",
            parse_mode="HTML"
        )
        return
    anime_list = await get_top_viewed_anime(10)
    if not anime_list:
        await message.answer("📭 Hozircha anime yo'q.")
        return
    await message.answer(
        "🔥 <b>Eng ko'p ko'rilgan animalar:</b>",
        parse_mode="HTML",
        reply_markup=anime_list_keyboard(anime_list)
    )


# ─── QIDIRUV JARAYONI ─────────────────────────────────────────────

@router.message(SearchState.waiting_name)
async def process_name_search(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("❗ Kamida 2 ta harf kiriting.")
        return

    results = await search_anime_by_name(query)
    if not results:
        await message.answer(f"❌ «{query}» bo'yicha hech narsa topilmadi.\n\nBoshqa nom bilan urinib ko'ring.")
        return

    if len(results) == 1:
        await send_anime_info(message, results[0])
    else:
        await message.answer(
            f"🔍 «{query}» bo'yicha <b>{len(results)}</b> ta natija topildi:",
            parse_mode="HTML",
            reply_markup=anime_list_keyboard(results)
        )


@router.message(SearchState.waiting_code)
async def process_code_search(message: Message, state: FSMContext):
    await state.clear()
    code = message.text.strip().upper()
    anime = await get_anime_by_code(code)
    if not anime:
        await message.answer(f"❌ <code>{code}</code> kodi bo'yicha anime topilmadi.", parse_mode="HTML")
        return
    await send_anime_info(message, anime)


@router.message(SearchState.waiting_genre)
async def process_genre_search(message: Message, state: FSMContext):
    await state.clear()
    genre = message.text.strip()
    results = await search_anime_by_genre(genre)
    if not results:
        await message.answer(f"❌ «{genre}» janri bo'yicha hech narsa topilmadi.")
        return
    await message.answer(
        f"🏷️ «{genre}» janrida <b>{len(results)}</b> ta anime:",
        parse_mode="HTML",
        reply_markup=anime_list_keyboard(results)
    )


# ─── ANIME MA'LUMOTLARI ───────────────────────────────────────────

async def send_anime_info(message: Message, anime: dict):
    """Anime ma'lumotlarini yuborish"""
    await increment_anime_views(anime["code"])

    # Reklama (VIP bo'lmagan foydalanuvchilar uchun)
    if not await is_vip(message.from_user.id):
        await message.answer(AD_TEXT, parse_mode="HTML")

    text = format_anime_info(anime)
    kb = anime_info_keyboard(anime["code"], anime.get("total_episodes", 0))

    if anime.get("poster_file_id"):
        await message.answer_photo(
            photo=anime["poster_file_id"],
            caption=text,
            parse_mode="HTML",
            reply_markup=kb,
            protect_content=True
        )
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("anime:"))
async def anime_by_callback(callback: CallbackQuery):
    code = callback.data.split(":")[1]
    anime = await get_anime_by_code(code)
    if not anime:
        await callback.answer("❌ Anime topilmadi!", show_alert=True)
        return
    await send_anime_info(callback.message, anime)
    await callback.answer()
