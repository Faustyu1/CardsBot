from aiogram.filters import BaseFilter
from aiogram.types import Message


class CardFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if message.text is not None and message.text.casefold() in \
                ["Карта".casefold(), "карта2".casefold(), "карта3".casefold(), "карта4".casefold(),
                 "карта5".casefold(), "/cards@юзернеймбота".casefold(), "/cards".casefold()]:    
            return True
        else:
            return False