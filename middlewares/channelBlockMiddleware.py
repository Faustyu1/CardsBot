from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.exceptions import TelegramBadRequest
from database.group import get_group
from data.text import post_msg

class BlockUserAndChannelMiddleware(BaseMiddleware):
    BLOCKED_USER_ID = 136817688

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.type == "channel":
            try:
                pass
            except TelegramBadRequest:
                pass
            return None

        if event.from_user and event.from_user.id == self.BLOCKED_USER_ID:
            try:
                pass
            except TelegramBadRequest:
                pass
            return None
        if event.is_automatic_forward:
            try:
                settings = await get_group(event.chat.id)
                if settings.comments_on:
                    await event.reply(post_msg, parse_mode="HTML")
            except TelegramBadRequest:
                pass
            return None

        return await handler(event, data)