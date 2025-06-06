from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database.user import get_user, upgrade_user, User as BotUser
from handlers.admin_dialogs.admin_states import AddAdminSG


async def on_get_id(
    message: Message, widget, dialog_manager: DialogManager, telegram_id: int
):
    user = await get_user(int(telegram_id))
    if user is not None and user.status == "ADMIN":
        await dialog_manager.switch_to(AddAdminSG.user_is_banned)
    elif user is not None:
        dialog_manager.dialog_data["user"] = user
        await dialog_manager.switch_to(AddAdminSG.accept)
    else:
        dialog_manager.dialog_data["error"] = "Пользователь не найден в базе данных"
        await dialog_manager.switch_to(AddAdminSG.error)


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
    await upgrade_user(user.telegram_id)
    await manager.switch_to(AddAdminSG.all_ok)


add_admin_dialog = Dialog(
    Window(
        Const("Введите айди пользователя которого необходимо повысить"),
        TextInput(type_factory=int, id="user_id", on_success=on_get_id),
        Cancel(Const("В меню")),
        state=AddAdminSG.get_id,
    ),
    Window(
        Const("Желаете повысить пользователя?"),
        Format("Имя: {username}"),
        Format("Айди: {user_id}"),
        Button(Const("Повысить"), id="__upgrade__", on_click=accept_clicked),
        Back(Const("Назад")),
        getter=accept_getter,
        state=AddAdminSG.accept,
    ),
    Window(
        Const("Пользователь успешно повышен"),
        Cancel(Const("В меню")),
        state=AddAdminSG.all_ok,
    ),
    Window(
        Const("Пользователь уже повышен"),
        Cancel(Const("В меню")),
        state=AddAdminSG.user_is_banned,
    ),
    Window(
        Format("Ошибка: {dialog_data[error]}"),
        Cancel(Const("В меню")),
        state=AddAdminSG.error,
    ),
)
