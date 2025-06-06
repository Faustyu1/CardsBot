from aiogram import Router

from middlewares import AdminMiddleware
from .base_dialogs import base_dialogs
from .ban_dialogs import ban_dialogs
from .add_admin_dialogs import add_admin_dialogs
from .promo_dialogs import promo_dialogs
from .ref_link_dialogs import ref_link_dialogs

dialogs_router = Router()

dialogs_router.include_routers(
    base_dialogs,
    ban_dialogs,
    add_admin_dialogs,
    promo_dialogs,
    ref_link_dialogs,
)
dialogs_router.message.middleware(AdminMiddleware())
dialogs_router.callback_query.middleware(AdminMiddleware())
