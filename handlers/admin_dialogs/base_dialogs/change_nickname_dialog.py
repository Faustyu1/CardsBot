from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database.user import get_user, unban_user, User as BotUser
from handlers.admin_dialogs.admin_states import UnBanSG


async def on_get_id(
    message: Message, widget, dialog_manager: DialogManager, telegram_id: int
):
    user = await get_user(telegram_id)
    if user is not None and not user.is_banned:
        await dialog_manager.switch_to(UnBanSG.user_not_banned)
    elif user is not None:
        dialog_manager.dialog_data["user"] = user
        await dialog_manager.switch_to(UnBanSG.accept)
    else:
        dialog_manager.dialog_data["error"] = "Пользователь не найден в базе данных"
        await dialog_manager.switch_to(UnBanSG.error)


async def accept_getter(
    dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs
):
    user: BotUser = dialog_manager.dialog_data["user"]
    return {
        "username": user.nickname,
        "user_id": user.telegram_id,
    }


async def accept_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: BotUser = manager.dialog_data["user"]
    await unban_user(user.telegram_id)
    await manager.switch_to(UnBanSG.all_ok)


change_nickname_dialog = Dialog(
    Window(
        Const("Введите айди пользователя которого необходимо разбанить"),
        TextInput(type_factory=int, id="user_id", on_success=on_get_id),
        Cancel(Const("В меню")),
        state=UnBanSG.get_id,
    ),
    Window(
        Const("Желаете разбанить пользователя?"),
        Format("Имя: {username}"),
        Format("Айди: {user_id}"),
        Button(Const("Разбанить"), id="__ban__", on_click=accept_clicked),
        Back(Const("Назад")),
        getter=accept_getter,
        state=UnBanSG.accept,
    ),
    Window(
        Const("Пользователь успешно разбанен"),
        Cancel(Const("В меню")),
        state=UnBanSG.all_ok,
    ),
    Window(
        Const("Пользователь не заблокирован"),
        Cancel(Const("В меню")),
        state=UnBanSG.user_not_banned,
    ),
    Window(
        Format("Ошибка: {dialog_data[error]}"),
        Cancel(Const("В меню")),
        state=UnBanSG.error,
    ),
)
