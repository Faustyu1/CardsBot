from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database.group import create_group, get_group, update_last_activity_group
from database.user import create_user, get_user, update_last_activity


class RegisterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        event: Message = event
        user = await get_user(event.from_user.id)
        if user is None:
            in_pm = True if event.chat.type == "private" else False
            data["user"] = await create_user(event.from_user.id, event.from_user.username, in_pm)
            created = True
        else:
            data["user"] = user
            created = False
            if event.chat.type == "private":
                await update_last_activity(event.from_user.id)
        if event.chat.type in ["group", "supergroup"]:
            if await get_group(event.chat.id) is None:
                await create_group(event.chat.id, event.chat.title)
                created = True
            else:
                created = False
                await update_last_activity_group(event.chat.id)
        if isinstance(event, Message) and event.text:
            if event.text.startswith("/start") or event.text.startswith("/startgroup"):
                data["created"] = created
                return await handler(event, data)

        return await handler(event, data)
