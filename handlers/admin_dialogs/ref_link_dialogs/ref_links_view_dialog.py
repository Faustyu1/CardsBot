import io
from typing import Any

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format, Jinja

from database import get_all_groups_with_bot_ids
from database.ref_link import delete_ref_link, get_all_links, get_links
from database.statistic import (
    get_all_users_with_link,
    get_groups_with_link_count,
    get_users_with_link_count,
)
from handlers.admin_dialogs.admin_states import ViewRefLinkSG


async def error(
    message: Message, dialog_: Any, manager: DialogManager, link_error: ValueError
):
    await message.answer(f"Произошла ошибка: {link_error.args[0]}")


async def all_link_getter(dialog_manager: DialogManager, bot: Bot, **kwargs):
    links = await get_all_links()
    return {"links": links}


async def on_provider_selected(
    callback: CallbackQuery, button: Button, manager: DialogManager, link: str
):
    manager.dialog_data["link_name"] = link
    await manager.switch_to(ViewRefLinkSG.one_link)


async def link_getter(dialog_manager: DialogManager, bot: Bot, **kwargs):
    link = dialog_manager.dialog_data["link_name"]
    links = await get_links(link, (await bot.get_me()).username)
    users_from_link = await get_users_with_link_count(link)
    groups_from_link = await get_groups_with_link_count(link)
    return {
        "link_name": link,
        "users_link": links["link_user"],
        "groups_link": links["link_group"],
        "users_from_link": users_from_link,
        "groups_from_link": groups_from_link,
    }


async def on_delete_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    link = manager.dialog_data["link_name"]
    await delete_ref_link(link)
    await manager.switch_to(ViewRefLinkSG.link_list)


async def on_upload_users_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    link = manager.dialog_data["link_name"]
    users_ids = await get_all_users_with_link(link)
    group_ids = "\n".join(str(user_id) for user_id in users_ids)
    await callback.message.answer_document(
        BufferedInputFile(io.BytesIO(group_ids.encode()).getbuffer(), "groups.txt")
    )


async def on_upload_groups_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    groups_ids = await get_all_groups_with_bot_ids()
    group_ids = "\n".join(str(group_id) for group_id in groups_ids)
    await callback.message.answer_document(
        BufferedInputFile(io.BytesIO(group_ids.encode()).getbuffer(), "groups.txt")
    )


view_links_dialog = Dialog(
    Window(
        Const("Список ссылок:"),
        ScrollingGroup(
            Select(
                Format("{item}"),
                id="choose_link_select",
                item_id_getter=lambda item: item,
                items="links",
                on_click=on_provider_selected,
            ),
            width=1,
            height=5,
            id="choose_link",
        ),
        Cancel(Const("В меню")),
        state=ViewRefLinkSG.link_list,
        getter=all_link_getter,
    ),
    Window(
        Jinja("Статистика ссылки {{link_name}}: \n\n"),
        Jinja(" -Переходы в лс: {{ users_from_link }}"),
        Jinja(" -Переходы в группы: {{ groups_from_link }}\n\n"),
        Jinja("<code>{{ users_link }}</code>\n\n"),
        Jinja("<code>{{ groups_link }}</code>"),
        Button(
            Const("Выгрузка юзеров"),
            id="download_users",
            on_click=on_upload_users_clicked,
        ),
        Button(
            Const("Выгрузка групп"),
            id="download_groups",
            on_click=on_upload_groups_clicked,
        ),
        Button(Const("Удалить"), id="delete_link", on_click=on_delete_clicked),
        Back(Const("Назад")),
        parse_mode=ParseMode.HTML,
        getter=link_getter,
        state=ViewRefLinkSG.one_link,
    ),
)
