from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db import get_anime_by_code, get_episodes_list, get_episode
from utils.keyboards import episodes_keyboard

router = Router()


@router.callback_query(F.data.startswith("episodes:"))
async def show_episodes(callback: CallbackQuery):
    parts = callback.data.split(":")
    anime_code = parts[1]
    page = int(parts[2]) if len(parts) > 2 else 1

    anime = await get_anime_by_code(anime_code)
    if not anime:
        await callback.answer("❌ Anime topilmadi!", show_alert=True)
        return

    episode_numbers = await get_episodes_list(anime_code)
    if not episode_numbers:
        await callback.answer("❌ Epizodlar hali qo'shilmagan!", show_alert=True)
        return

    kb = episodes_keyboard(anime_code, episode_numbers, page)
    name = anime.get("name_uz") or anime.get("name_en", "Anime")

    text = (
        f"📺 <b>{name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Jami: <b>{len(episode_numbers)}</b> ta epizod\n\n"
        f"▶️ Ko'rmoqchi bo'lgan epizodingizni tanlang:"
    )

    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)

    await callback.answer()


@router.callback_query(F.data.startswith("watch:"))
async def watch_episode(callback: CallbackQuery):
    parts = callback.data.split(":")
    anime_code = parts[1]
    episode_number = int(parts[2])

    episode = await get_episode(anime_code, episode_number)
    if not episode:
        await callback.answer("❌ Bu epizod hali mavjud emas!", show_alert=True)
        return

    anime = await get_anime_by_code(anime_code)
    name = anime.get("name_uz") or anime.get("name_en", "Anime") if anime else anime_code

    caption = (
        f"🎬 <b>{name}</b>\n"
        f"📺 <b>{episode_number}-epizod</b>"
    )
    if episode.get("title"):
        caption += f"\n🏷️ {episode['title']}"

    await callback.message.answer_video(
        video=episode["video_file_id"],
        caption=caption,
        parse_mode="HTML",
        protect_content=True  # Yuborishdan himoya
    )
    await callback.answer()


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
