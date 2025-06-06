from aiogram import Router

from .ref_links_view_dialog import view_links_dialog
from .ref_links_add_dialog import ref_links_add_dialog

ref_link_dialogs = Router()
ref_link_dialogs.include_routers(view_links_dialog, ref_links_add_dialog)
