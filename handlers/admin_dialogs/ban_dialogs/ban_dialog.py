from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database.user import ban_user, get_user, User as BotUser
from handlers.admin_dialogs.admin_states import BanSG


async def on_get_id(
    message: Message, widget, dialog_manager: DialogManager, telegram_id: int
):
    user = await get_user(telegram_id)
    if user is not None and user.is_banned:
        await dialog_manager.switch_to(BanSG.user_is_banned)
    elif user is not None:
        dialog_manager.dialog_data["user"] = user
        await dialog_manager.switch_to(BanSG.accept)
    else:
        dialog_manager.dialog_data["error"] = "Пользователь не найден в базе данных"
        await dialog_manager.switch_to(BanSG.error)


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
    await ban_user(user.telegram_id)
    await manager.switch_to(BanSG.all_ok)


ban_dialog = Dialog(
    Window(
        Const("Введите айди пользователя которого необходимо забанить"),
        TextInput(type_factory=int, id="user_id", on_success=on_get_id),
        Cancel(Const("В меню")),
        state=BanSG.get_id,
    ),
    Window(
        Const("Желаете забанить пользователя?"),
        Format("Имя: {username}"),
        Format("Айди: {user_id}"),
        Button(Const("Забанить"), id="__ban__", on_click=accept_clicked),
        Back(Const("Назад")),
        getter=accept_getter,
        state=BanSG.accept,
    ),
    Window(
        Const("Пользователь успешно забанен"),
        Cancel(Const("В меню")),
        state=BanSG.all_ok,
    ),
    Window(
        Const("Пользователь уже забанен"),
        Cancel(Const("В меню")),
        state=BanSG.user_is_banned,
    ),
    Window(
        Format("Ошибка: {dialog_data[error]}"),
        Cancel(Const("В меню")),
        state=BanSG.error,
    ),
)
