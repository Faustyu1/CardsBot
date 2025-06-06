from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import Animation, CallbackQuery, Message, PhotoSize, User, Video
from aiogram_dialog import ChatEvent, Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Checkbox,
    ManagedCheckbox,
    Next,
    Row,
)
from aiogram_dialog.widgets.text import Const

from utils.mailing import mailing
from handlers.admin_dialogs.admin_states import MailingSG


async def check_changed(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager
):
    manager.dialog_data[checkbox.widget.widget_id] = checkbox.is_checked()


async def media_handler(
    message: Message, message_input: MessageInput, manager: DialogManager
):
    if message.animation is not None:
        manager.dialog_data["media"] = message.animation
    elif message.video is not None:
        manager.dialog_data["media"] = message.video
    elif message.photo is not None:
        manager.dialog_data["media"] = message.photo
    await manager.switch_to(MailingSG.send_message)


async def skip_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data["media"] = None
    await manager.switch_to(MailingSG.send_message)


async def next_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    private = manager.find("__private__").is_checked()
    group = manager.find("__groups__").is_checked()
    if not private and not group:
        await manager.switch_to(MailingSG.error)
    else:
        await manager.switch_to(MailingSG.get_message)


async def accept_getter(
    dialog_manager: DialogManager, event_from_user: User, bot: Bot, **kwargs
):
    media = dialog_manager.dialog_data["media"]
    message_text = dialog_manager.find("message_text").get_value()
    if media:
        if type(media) is Animation:
            await bot.send_animation(
                event_from_user.id, animation=media.file_id, caption=message_text
            )
        elif type(media) is Video:
            await bot.send_video(
                event_from_user.id, video=media.file_id, caption=message_text
            )
        elif type(media[-1]) is PhotoSize:
            await bot.send_photo(
                event_from_user.id, photo=media[-1].file_id, caption=message_text
            )
    else:
        await bot.send_message(event_from_user.id, message_text)
    return {}


async def send_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    private = manager.find("__private__").is_checked()
    groups = manager.find("__groups__").is_checked()
    media = manager.dialog_data["media"]
    message_text = manager.find("message_text").get_value()
    await mailing(groups, private, media, message_text, callback.bot)
    await manager.done()


mailing_dialog = Dialog(
    Window(
        Const("Выберите тип чатов для рассылки"),
        Row(
            Checkbox(
                Const("✔ ЛС"),
                Const("❌ ЛС"),
                id="__private__",
                default=False,
                on_state_changed=check_changed,
            ),
            Checkbox(
                Const("✔ Группы"),
                Const("❌ Группы"),
                id="__groups__",
                default=False,
                on_state_changed=check_changed,
            ),
        ),
        Button(Const("Далее"), id="__next__", on_click=next_clicked),
        Cancel(Const("Назад")),
        state=MailingSG.choose_type,
    ),
    Window(
        Const("Введите текст сообщение (без медиа)"),
        TextInput(id="message_text", on_success=Next()),
        Back(Const("Назад")),
        state=MailingSG.get_message,
    ),
    Window(
        Const('Отправьте медиа или нажмите "Пропустить"'),
        MessageInput(
            media_handler,
            content_types=[ContentType.PHOTO, ContentType.VIDEO, ContentType.ANIMATION],
        ),
        Button(Const("Пропустить"), id="__skip__", on_click=skip_clicked),
        Back(Const("Назад")),
        state=MailingSG.get_media,
    ),
    Window(
        Const(
            'Ниже вы увидите как будет выглядеть ваше сообщение, если желаете его разослать нажмите "Отправить"'
        ),
        Button(Const("Отправить"), id="__send__", on_click=send_clicked),
        state=MailingSG.send_message,
    ),
    Window(
        Const("Пользователь, вы не выбрали не один тип чатов"),
        Cancel(Const("В меню")),
        state=MailingSG.error,
    ),
)
