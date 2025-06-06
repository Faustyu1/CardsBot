from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Format

from database.models import Promo
from database.promo import delete_promo, get_promo
from handlers.admin_dialogs.admin_states import DeletePromoSG


async def get_promo_name(
    message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, data: str
):
    promo = await get_promo(data)
    if promo is None:
        await message.answer("Промокод не найден")
        return
    else:
        dialog_manager.dialog_data["promo"] = promo
        await dialog_manager.switch_to(DeletePromoSG.accept)


async def accept_getter(
    dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs
):
    promo: Promo = dialog_manager.dialog_data["promo"]
    return {"promo": promo.code}


async def accept_clicked(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    promo = dialog_manager.dialog_data["promo"]
    await delete_promo(promo.code)
    await dialog_manager.switch_to(DeletePromoSG.all_ok)


delete_promo_dialog = Dialog(
    Window(
        Format("Введите название промокода, который хотите удалить"),
        TextInput(id="name", on_success=get_promo_name),
        Cancel(Format("В меню")),
        state=DeletePromoSG.get_name,
    ),
    Window(
        Format("Хотите удалить промокод {promo}?"),
        Button(Format("Удалить"), id="__accept__", on_click=accept_clicked),
        getter=accept_getter,
        state=DeletePromoSG.accept,
    ),
    Window(
        Format("Промокод успешно удален"),
        Cancel(Format("В меню")),
        state=DeletePromoSG.all_ok,
    ),
)
