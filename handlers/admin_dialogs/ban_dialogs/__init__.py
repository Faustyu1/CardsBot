from aiogram import Router

from .ban_dialog import ban_dialog
from .unban_dialog import unban_dialog

ban_dialogs = Router()
ban_dialogs.include_routers(ban_dialog, unban_dialog)
