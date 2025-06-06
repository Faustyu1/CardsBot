from aiogram import Router

from .delete_promo_dialog import delete_promo_dialog
from .create_promo_dialog import add_promo_dialog

promo_dialogs = Router()
promo_dialogs.include_routers(add_promo_dialog, delete_promo_dialog)
