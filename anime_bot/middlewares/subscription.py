from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest


class SubscriptionMiddleware(BaseMiddleware):
    """Foydalanuvchi ma'lumotlarini ro'yxatdan o'tkazish middleware"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Foydalanuvchini bazaga yozish
        from database import register_user
        user = event.from_user
        if user:
            register_user(
                telegram_id=user.id,
                username=user.username or "",
                full_name=user.full_name or ""
            )
        return await handler(event, data)
