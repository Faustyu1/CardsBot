import asyncio

from aiogram import Dispatcher
from aiogram.types import BotCommand
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import DialogManager, setup_dialogs
from middlewares.channelBlockMiddleware import BlockUserAndChannelMiddleware
from utils.logger import *
import logging

from utils import loader
from database import setup_db
from database.cards import parse_cards, parse_limited_cards
from handlers import commands_router, premium_router, profile_router, text_triggers_router, shop_router, shop_cards_router
from handlers.admin_dialogs import dialogs_router
from utils.loader import bot
from middlewares import BannedMiddleware, RegisterMiddleware, ThrottlingMiddleware
from utils.on_startup import on_startup

dp = Dispatcher(storage=MemoryStorage(), on_startup=on_startup)
logger = logging.getLogger(__name__)

async def main():
    await setup_db()
    dp.include_routers(commands_router, profile_router, 
                       premium_router, shop_router, 
                       dialogs_router, shop_cards_router,
                       text_triggers_router)
    setup_dialogs(dp)
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(RegisterMiddleware())
    dp.message.middleware(BannedMiddleware())
    dp.message.middleware(BlockUserAndChannelMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="profile", description="Ваш профиль"),
        BotCommand(command="cards", description="Получить карточку"),
        BotCommand(command="help", description="📜 Помощь"),
        BotCommand(command="profile", description="👤 Ваш профиль"),
        BotCommand(command="cards", description="🃏 Получить карточку"),
        BotCommand(command="top", description="🏆 Топ игроков"),
        BotCommand(command="premium", description="🚀 Купить премиум"),
        BotCommand(command="shop", description="🛍 Игровой магазин"),
        BotCommand(command="diceplay", description="🎲 Испытать удачу"),
    ]
    await bot.set_my_commands(commands)
    dp.startup.register(on_startup)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())