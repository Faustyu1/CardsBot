from aiogram import Router

from .admin_dialog import admin_dialog
from .mailing_dialog import mailing_dialog
from .premium_dialog import premium_dialog
from .season_delete_dialog import season_delete_dialog
from .change_nickname_dialog import change_nickname_dialog


base_dialogs = Router()
base_dialogs.include_routers(
    admin_dialog,
    mailing_dialog,
    premium_dialog,
    season_delete_dialog,
    change_nickname_dialog,
)
