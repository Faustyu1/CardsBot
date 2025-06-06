from aiogram.filters import BaseFilter
from aiogram.types import Message


class NotCommentFilter(BaseFilter):
    async def check_first_message(self, message: Message) -> bool:
        if message.reply_to_message is not None:
            await self.check_first_message(message.reply_to_message)
        else:
            return message

    async def __call__(self, message: Message) -> bool:
        first_message: Message = await self.check_first_message(message)
        if first_message is None:
            return True
        if first_message.chat.type != "channel":
            return True
        else:
            return False
