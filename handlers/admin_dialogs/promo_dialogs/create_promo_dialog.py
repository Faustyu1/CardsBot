from datetime import date, datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Calendar, Cancel, Next, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from database.promo import create_promo, get_promo
from handlers.admin_dialogs.admin_states import CreatePromoSG


async def get_promo_name(
    message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, data: str
):
    promo = await get_promo(dialog_manager.find("name").get_value())
    if promo is None:
        dialog_manager.dialog_data["name"] = data
        await dialog_manager.switch_to(CreatePromoSG.get_action)
    else:
        await message.answer(
            "Промокод с таким названием уже существует, попробуйте ещё раз"
        )


async def reset_cd_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    manager.dialog_data["action"] = "reset_cd"
    await manager.switch_to(CreatePromoSG.get_expiration_time)


async def add_premium_clicked(
    callback: Message, button: Button, manager: DialogManager
):
    manager.dialog_data["action"] = "add_premium"
    await manager.switch_to(CreatePromoSG.get_premium_days)


async def get_channel_func(
    message: Message, message_input: MessageInput, manager: DialogManager
):
    if message.forward_origin is None:
        await message.answer("Это сообщение не переслано")
        return
    try:
        channel_bot_member = await message.bot.get_chat_member(
            message.forward_origin.chat.id, message.bot.id
        )
    except Exception:
        await message.answer("Вероятно бот отсутствует в пересланном канале")
        return
    channel = await message.bot.get_chat(message.forward_origin.chat.id)
    if channel.type != "channel":
        await message.answer("Это не канал")
        return
    channel_link = (await message.bot.create_chat_invite_link(channel.id)).invite_link
    manager.dialog_data["channel"] = channel_link
    manager.dialog_data["channel_id"] = channel.id
    await manager.switch_to(CreatePromoSG.accept)


async def on_date_selected(
    callback: CallbackQuery, widget, manager: DialogManager, selected_date: date
):
    manager.dialog_data["expiration_str"] = selected_date.strftime("%d.%m.%Y")
    manager.dialog_data["expiration_date"] = selected_date
    await manager.switch_to(CreatePromoSG.get_activation_limit)


async def accept_getter(
    dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs
):
    promo_name = dialog_manager.find("name").get_value()
    action = dialog_manager.dialog_data["action"]
    if action == "add_premium":
        premium_days = dialog_manager.find("premium_days").get_value()
        show_days = True
    else:
        premium_days = None
        show_days = False
    match action:
        case "reset_cd":
            action_str = "Сброс кд"
        case "add_premium":
            action_str = "Премиум на " + str(premium_days) + " дней"
        case _:
            raise ValueError("Unknown action")
    expiration_str: datetime = dialog_manager.dialog_data["expiration_str"]
    activation_limit = dialog_manager.find("activation_limit").get_value()
    channel = dialog_manager.dialog_data["channel"]
    print(expiration_str)
    return {
        "promo_name": promo_name,
        "action": action_str,
        "premium_days": premium_days,
        "expiration_str": expiration_str,
        "activation_limit": activation_limit,
        "channel": channel,
    }


async def accept_clicked(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    promo_name = dialog_manager.find("name").get_value()
    action = dialog_manager.dialog_data["action"]
    if action == "add_premium":
        premium_days = dialog_manager.find("premium_days").get_value()
    else:
        premium_days = None

    expiration_date: datetime = dialog_manager.dialog_data["expiration_date"]
    activation_limit = dialog_manager.find("activation_limit").get_value()
    channel = dialog_manager.dialog_data["channel"]
    channel_id = dialog_manager.dialog_data["channel_id"]
    try:
        await create_promo(
            code=promo_name,
            link=channel,
            action=action,
            days_add=premium_days,
            activation_limit=activation_limit,
            expiration_time=expiration_date,
            channel_id=channel_id,
        )
        await dialog_manager.switch_to(CreatePromoSG.all_ok)
    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
        await dialog_manager.done()


add_promo_dialog = Dialog(
    Window(
        Format("Введите название промокода"),
        TextInput(id="name", on_success=get_promo_name),
        Cancel(Const("В меню")),
        state=CreatePromoSG.get_name,
    ),
    Window(
        Format("Выберите действие"),
        Button(Const("Сброс кд"), id="__reset__", on_click=reset_cd_clicked),
        Button(
            Const("Добавить премиум"),
            id="__add_premium__",
            on_click=add_premium_clicked,
        ),
        Back(Const("Назад")),
        state=CreatePromoSG.get_action,
    ),
    Window(
        Format("Введите количество дней премиума"),
        TextInput(type_factory=int, id="premium_days", on_success=Next()),
        Back(Const("Назад")),
        state=CreatePromoSG.get_premium_days,
    ),
    Window(
        Format("Введите время действия промокода"),
        Calendar(id="calendar", on_click=on_date_selected),
        SwitchTo(Const("Назад"), id="__back__", state=CreatePromoSG.get_action),
        state=CreatePromoSG.get_expiration_time,
    ),
    Window(
        Format("Введите количество активации"),
        TextInput(id="activation_limit", on_success=Next(), type_factory=int),
        Back(Const("Назад")),
        state=CreatePromoSG.get_activation_limit,
    ),
    Window(
        Format("Добавьте бота в необходимый канал и перешлите оттуда сообщение"),
        MessageInput(func=get_channel_func),
        Back(Const("Назад")),
        state=CreatePromoSG.get_channel,
    ),
    Window(
        Format("Хотите создать промо?"),
        Format("Название: {promo_name}"),
        Format("Действие: {action}"),
        Format("Время действия: до {expiration_str}"),
        Format("Количество активации: {activation_limit}"),
        Format("Канал (ссылка): {channel}"),
        Button(Const("Создать"), id="__accept__", on_click=accept_clicked),
        Back(Const("Назад")),
        getter=accept_getter,
        state=CreatePromoSG.accept,
    ),
    Window(
        Const("Промо успешно создано!"),
        Cancel(Const("В меню")),
        state=CreatePromoSG.all_ok,
    ),
)
