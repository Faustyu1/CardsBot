import asyncio
import logging
from typing import Optional, Callable, Union, List

from aiogram import Bot
from aiogram.types import Animation, PhotoSize, Video
from aiogram.exceptions import TelegramAPIError

from database.group import get_all_groups_with_bot_ids
from database.user import get_all_users_with_pm_ids

logger = logging.getLogger(__name__)

class MessageDispatcher:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.rate_limit = 25  # messages per second
        self.retry_count = 3

    async def _get_send_method(self, media: Optional[Union[Animation, Video, List[PhotoSize]]]) -> Callable:
        if not media:
            return self.bot.send_message
        
        media_type_mapping = {
            Animation: self.bot.send_animation,
            Video: self.bot.send_video,
            list: self.bot.send_photo if isinstance(media[-1], PhotoSize) else self.bot.send_message
        }
        return media_type_mapping.get(type(media), self.bot.send_message)

    async def _send_with_retry(self, chat_id: int, send_method: Callable, media, text: str) -> bool:
        for attempt in range(self.retry_count):
            try:
                if media:
                    await send_method(
                        chat_id=chat_id,
                        file_id=media.file_id if hasattr(media, 'file_id') else media,
                        caption=text,
                        parse_mode='Markdown'
                    )
                else:
                    await send_method(
                        chat_id=chat_id,
                        text=text,
                        parse_mode='Markdown'
                    )
                return True
                
            except TelegramAPIError as e:
                logger.error(f"Failed to send message to {chat_id} (attempt {attempt + 1}): {str(e)}")
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(1)
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error sending to {chat_id}: {str(e)}")
                return False
        
        return False

    async def _dispatch_messages(self, recipients: List[int], send_method: Callable, media, text: str):
        tasks = []
        for chat_id in recipients:
            tasks.append(self._send_with_retry(chat_id, send_method, media, text))
            
            if len(tasks) >= self.rate_limit:
                await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)  # Rate limiting
                
        if tasks:
            await asyncio.gather(*tasks)

    async def send_mailing(self, send_to_groups: bool, send_to_dm: bool, media, text: str):
        """
        Send mass mailing to specified recipients.
        
        Args:
            send_to_groups (bool): Whether to send to groups
            send_to_dm (bool): Whether to send to direct messages
            media: Optional media content (Animation, Video, or PhotoSize)
            text (str): Message text or media caption
        """
        send_method = await self._get_send_method(media)
        
        if send_to_groups:
            groups = await get_all_groups_with_bot_ids()
            logger.info(f"Starting group mailing to {len(groups)} recipients")
            await self._dispatch_messages(groups, send_method, media, text)
            
        if send_to_dm:
            users = await get_all_users_with_pm_ids()
            logger.info(f"Starting DM mailing to {len(users)} recipients")
            await self._dispatch_messages(users, send_method, media, text)

async def mailing(send_on_groups: bool, send_dm: bool, media, text: str, bot: Bot):
    """
    Main mailing function.
    
    Args:
        send_on_groups (bool): Whether to send to groups
        send_dm (bool): Whether to send to direct messages
        media: Optional media content
        text (str): Message text
        bot (Bot): Aiogram Bot instance
    """
    dispatcher = MessageDispatcher(bot)
    await dispatcher.send_mailing(send_on_groups, send_dm, media, text)