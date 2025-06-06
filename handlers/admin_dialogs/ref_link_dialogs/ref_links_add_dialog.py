import re
from typing import Any

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.text import Jinja

from database.ref_link import create_ref_link, get_links, get_ref_link
from handlers.admin_dialogs.admin_states import AddRefLinkSG


def check_link(link: str) -> str:
    if len(link) > 16:
        raise ValueError("Слишком длинная ссылка")
    if not re.fullmatch(r"[A-Za-z0-9\-]+", link):
        raise ValueError("Ссылка содержит недопустимые символы")
    return link


async def error(
    message: Message, dialog_: Any, manager: DialogManager, link_error: ValueError
):
    await message.answer(f"Произошла ошибка: {link_error.args[0]}")


async def link_created_getter(dialog_manager: DialogManager, bot: Bot, **kwargs):
    link = dialog_manager.find("link_name").get_value()
    bot_username = (await bot.get_me()).username
    await create_ref_link(link)
    links = await get_links(link, bot_username)
    return {"users_link": links["link_user"], "groups_link": links["link_group"]}


async def on_success(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data_,
    **kwargs,
):
    link = await get_ref_link(widget.get_value())
    if link is not None:
        await dialog_manager.switch_to(AddRefLinkSG.error)
    else:
        await dialog_manager.switch_to(AddRefLinkSG.all_ok)


ref_links_add_dialog = Dialog(
    Window(
        Const("Введите имя новой ссылки:"),
        TextInput(
            id="link_name",
            type_factory=check_link,
            on_success=on_success,
            on_error=error,
        ),
        Cancel(Const("В меню")),
        state=AddRefLinkSG.get_link,
    ),
    Window(
        Format("Ссылка успешно зарегистрирована!"),
        Jinja("<code>{{ users_link }}</code>\n\n"),
        Jinja("<code>{{ groups_link }}</code>"),
        Cancel(Const("В меню")),
        parse_mode=ParseMode.HTML,
        getter=link_created_getter,
        state=AddRefLinkSG.all_ok,
    ),
    Window(
        Jinja("Ошибка! Cсылка уже зарегистрирована!"),
        Cancel(Const("В меню")),
        SwitchTo(Const("Создать ссылку"), id="reboot", state=AddRefLinkSG.get_link),
        state=AddRefLinkSG.error,
    ),
)
