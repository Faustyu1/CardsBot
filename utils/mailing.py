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
        # Статистика рассылки
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "deactivated_users": 0,
            "blocked_bots": 0,
            "not_found_chats": 0,
            "format_errors": 0,
            "other_errors": 0
        }

    def _sanitize_markdown(self, text: str) -> str:
        """
        Исправляет проблемы с Markdown-разметкой.
        
        Args:
            text: Исходный текст с возможно некорректной Markdown-разметкой
            
        Returns:
            Исправленный текст с корректной Markdown-разметкой
        """
        import re
        if not text:
            return ""
            
        # Проверка наличия незакрытых символов разметки
        markers = ['*', '_', '`', '[']
        for marker in markers:
            count = text.count(marker)
            if count % 2 != 0:
                # Если нечетное количество маркеров, экранируем последний
                last_pos = text.rindex(marker)
                text = text[:last_pos] + '\\' + text[last_pos:]
                
        # Проверка корректности url-ссылок
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, text):
            link_text, url = match.groups()
            if not url.startswith(('http://', 'https://', 'tg://')):
                # Заменяем некорректную ссылку на простой текст
                old = f'[{link_text}]({url})'
                new = f'{link_text} ({url})'
                text = text.replace(old, new)
                
        return text

    async def _get_send_method(self, media: Optional[Union[Animation, Video, List[PhotoSize]]]):
        if media is None:
            return self.bot.send_message, False
        
        if isinstance(media, Animation):
            return self.bot.send_animation, True
        elif isinstance(media, Video):
            return self.bot.send_video, True
        elif isinstance(media, list) and media and isinstance(media[0], PhotoSize):
            return self.bot.send_photo, True
        else:
            return self.bot.send_message, False

    async def _send_with_retry(self, chat_id: int, send_method: Callable, media, text: str) -> bool:
        # Санитизируем текст перед отправкой
        sanitized_text = self._sanitize_markdown(text)
        
        for attempt in range(self.retry_count):
            try:
                if isinstance(media, list) and media and isinstance(media[0], PhotoSize):
                    # Для списка фотографий берем самую большую (обычно последнюю)
                    file_id = sorted(media, key=lambda p: p.width * p.height, reverse=True)[0].file_id
                    await send_method(
                        chat_id=chat_id,
                        photo=file_id,
                        caption=sanitized_text,
                        parse_mode='Markdown'
                    )
                elif isinstance(media, Animation):
                    await send_method(
                        chat_id=chat_id,
                        animation=media.file_id,
                        caption=sanitized_text,
                        parse_mode='Markdown'
                    )
                elif isinstance(media, Video):
                    await send_method(
                        chat_id=chat_id,
                        video=media.file_id,
                        caption=sanitized_text,
                        parse_mode='Markdown'
                    )
                else:
                    await send_method(
                        chat_id=chat_id,
                        text=sanitized_text,
                        parse_mode='Markdown'
                    )
                self.stats["total_sent"] += 1
                return True
                
            except TelegramAPIError as e:
                error_msg = str(e).lower()
                
                # Если пользователь деактивирован или заблокировал бота - просто пропускаем
                if "forbidden: bot was blocked by the user" in error_msg:
                    logger.info(f"Bot was blocked by user {chat_id} - skipping")
                    self.stats["blocked_bots"] += 1
                    return False
                elif "forbidden: user is deactivated" in error_msg:
                    logger.info(f"User {chat_id} is deactivated - skipping")
                    self.stats["deactivated_users"] += 1
                    return False
                elif "bad request: chat not found" in error_msg:
                    logger.info(f"Chat {chat_id} not found - skipping")
                    self.stats["not_found_chats"] += 1
                    return False
                
                # Обрабатываем ошибки форматирования
                if "can't parse entities" in error_msg:
                    logger.error(f"Failed to send message to {chat_id} (attempt {attempt + 1}): {str(e)}")
                    
                    # При последней попытке пробуем отправить без разметки
                    if attempt == self.retry_count - 1:
                        try:
                            if media:
                                if isinstance(media, list) and isinstance(media[0], PhotoSize):
                                    file_id = sorted(media, key=lambda p: p.width * p.height, reverse=True)[0].file_id
                                    await self.bot.send_photo(chat_id=chat_id, photo=file_id, caption=text)
                                elif isinstance(media, Animation):
                                    await self.bot.send_animation(chat_id=chat_id, animation=media.file_id, caption=text)
                                elif isinstance(media, Video):
                                    await self.bot.send_video(chat_id=chat_id, video=media.file_id, caption=text)
                            else:
                                await self.bot.send_message(chat_id=chat_id, text=text)
                            self.stats["total_sent"] += 1
                            return True
                        except Exception as fallback_error:
                            logger.error(f"Failed fallback sending to {chat_id}: {str(fallback_error)}")
                            self.stats["format_errors"] += 1
                            return False
                    
                    if attempt < self.retry_count - 1:
                        await asyncio.sleep(1)
                    continue
                
                # Другие ошибки API Telegram
                logger.error(f"Failed to send message to {chat_id} (attempt {attempt + 1}): {str(e)}")
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(1)
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error sending to {chat_id}: {str(e)}")
                self.stats["other_errors"] += 1
                return False
        
        self.stats["total_failed"] += 1
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
            
        Returns:
            dict: Статистика рассылки
        """
        # Сбрасываем статистику перед новой рассылкой
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "deactivated_users": 0,
            "blocked_bots": 0,
            "not_found_chats": 0,
            "format_errors": 0,
            "other_errors": 0
        }
        
        send_method, _ = await self._get_send_method(media)
        
        if send_to_groups:
            groups = await get_all_groups_with_bot_ids()
            self.stats["total_groups"] = len(groups)
            logger.info(f"Starting group mailing to {len(groups)} recipients")
            await self._dispatch_messages(groups, send_method, media, text)
            
        if send_to_dm:
            users = await get_all_users_with_pm_ids()
            self.stats["total_users"] = len(users)
            logger.info(f"Starting DM mailing to {len(users)} recipients")
            await self._dispatch_messages(users, send_method, media, text)
            
        return self.stats

async def mailing(send_on_groups: bool, send_dm: bool, media, text: str, bot: Bot):
    """
    Main mailing function.
    
    Args:
        send_on_groups (bool): Whether to send to groups
        send_dm (bool): Whether to send to direct messages
        media: Optional media content
        text (str): Message text
        bot (Bot): Aiogram Bot instance
        
    Returns:
        dict: Статистика рассылки
    """
    dispatcher = MessageDispatcher(bot)
    stats = await dispatcher.send_mailing(send_on_groups, send_dm, media, text)
    
    logger.info(f"Mailing completed. Stats: {stats}")
    return stats
