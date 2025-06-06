from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database.user import change_username, get_user, User as BotUser
from handlers.admin_dialogs.admin_states import ChangeUsernameSG


async def on_get_id(
    message: Message, widget, dialog_manager: DialogManager, telegram_id: int
):
    user = await get_user(telegram_id)
    if user is not None:
        dialog_manager.dialog_data["user"] = user
        await dialog_manager.switch_to(ChangeUsernameSG.get_new_username)
    else:
        dialog_manager.dialog_data["error"] = "Пользователь не найден в базе данных"
        await dialog_manager.switch_to(ChangeUsernameSG.error)


async def get_username_getter(
    dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs
):
    user: BotUser = dialog_manager.dialog_data["user"]
    return {
        "username": user.nickname,
        "user_id": user.telegram_id,
    }


async def on_get_username(
    message: Message, widget, dialog_manager: DialogManager, username: str
):
    dialog_manager.dialog_data["username"] = username
    await dialog_manager.switch_to(ChangeUsernameSG.accept)


async def accept_getter(
    dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs
):
    user: BotUser = dialog_manager.dialog_data["user"]
    username: str = dialog_manager.dialog_data["username"]
    return {
        "old_username": user.nickname,
        "user_id": user.telegram_id,
        "new_username": username,
    }


async def accept_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: BotUser = manager.dialog_data["user"]
    username: str = manager.dialog_data["username"]
    await change_username(user.telegram_id, username)
    await manager.switch_to(ChangeUsernameSG.changed)


unban_dialog = Dialog(
    Window(
        Const("Введите айди пользователя"),
        TextInput(type_factory=int, id="user_id", on_success=on_get_id),
        Cancel(Const("В меню")),
        state=ChangeUsernameSG.get_id,
    ),
    Window(
        Const("Введите новое имя пользователя"),
        Format("Текущее имя: {username}"),
        Format("Айди: {user_id}"),
        TextInput(id="__username__", on_success=on_get_username),
        Back(Const("Назад")),
        getter=get_username_getter,
        state=ChangeUsernameSG.get_new_username,
    ),
    Window(
        Format(
            "Хотите сменить имя пользователю?\nАйди: {user_id}\nСтарый юзернейм: {old_username}\n"
            "Новый юзернейм: {new_username}"
        ),
        Button(Const("Сменить"), id="__accept__", on_click=accept_clicked),
        Back(Const("В меню")),
        getter=accept_getter,
        state=ChangeUsernameSG.accept,
    ),
    Window(
        Const("Юзернейм пользователя успешно изменен!"),
        Cancel(Const("В меню")),
        state=ChangeUsernameSG.changed,
    ),
)
