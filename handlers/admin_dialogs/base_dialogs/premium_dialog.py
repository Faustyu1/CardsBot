from datetime import date, datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Calendar, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database.models import User as BotUser
from database.premium import premium_from_datetime
from database.user import get_user
from handlers.admin_dialogs.admin_states import PremiumSG


async def on_get_id(
    message: Message, widget, dialog_manager: DialogManager, telegram_id: int
):
    user = await get_user(telegram_id)
    if user is not None:
        dialog_manager.dialog_data["user"] = user
        await dialog_manager.switch_to(PremiumSG.premium_get_date)
    else:
        dialog_manager.dialog_data["error"] = "Пользователь не найден в базе данных"
        await dialog_manager.switch_to(PremiumSG.error)


async def on_date_selected(
    callback: CallbackQuery, widget, manager: DialogManager, selected_date: date
):
    now = datetime.now().time()
    manager.dialog_data["end_date"] = datetime(
        year=selected_date.year,
        month=selected_date.month,
        day=selected_date.day,
        hour=now.hour,
        minute=now.minute,
    )
    await manager.next()


async def accept_premium_getter(
    dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs
):
    user: BotUser = dialog_manager.dialog_data["user"]
    end_data = dialog_manager.dialog_data["end_date"]
    return {
        "username": user.nickname,
        "user_id": user.telegram_id,
        "premium_end": str(end_data),
        "old_premium": user.premium_expire,
    }


async def accept_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: BotUser = manager.dialog_data["user"]
    end_date = manager.dialog_data["end_date"]
    await premium_from_datetime(user.telegram_id, end_date)
    await manager.switch_to(PremiumSG.all_good)


premium_dialog = Dialog(
    Window(
        Const(
            "Введите айди телеграм аккаунта пользователя которому необходимо выдать премиум"
        ),
        TextInput(type_factory=int, id="user_id", on_success=on_get_id),
        Cancel(Const("В меню")),
        state=PremiumSG.premium_get_id,
    ),
    Window(
        Const("Выберите день окончания действия премиума"),
        Calendar(id="end_date", on_click=on_date_selected),
        Back(Const("Назад")),
        state=PremiumSG.premium_get_date,
    ),
    Window(
        Const("Хотите выдать премиум статус пользователю?"),
        Format("Имя пользователя: {username}"),
        Format("Айди: {user_id}"),
        Format("Дата окончания подписки: {premium_end}"),
        Format("Старая дата окончания подписки: {old_premium}"),
        Button(Const("Выдать"), id="give_premium", on_click=accept_clicked),
        Back(Const("Назад")),
        getter=accept_premium_getter,
        state=PremiumSG.premium_accept,
    ),
    Window(
        Const("Все вышло!Можно возвращаться в меню"),
        Cancel(Const("В меню")),
        state=PremiumSG.all_good,
    ),
    Window(
        Format("Ошибка: {dialog_data[error]}"),
        Cancel(Const("В меню")),
        state=PremiumSG.error,
    ),
)
