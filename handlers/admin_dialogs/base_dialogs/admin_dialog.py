import datetime
import datetime
import io

from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Next, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi

from database.group import get_all_groups_with_bot_ids, get_group_with_bot_count
from database.statistic import get_groups_count_created_by_date, get_groups_count_last_active_today, \
    get_users_count_created_by_date, \
    get_users_count_last_active_today, get_yesterday_groups_active, get_yesterday_users_active
from database.user import get_all_users_with_pm_ids, get_user_with_pm_count
from handlers.admin_dialogs.admin_states import AddAdminSG, AddRefLinkSG, AdminSG, CreatePromoSG, DelSeasonSG, DeletePromoSG, MailingSG, ViewRefLinkSG


async def message_to_mailing_handler(message: Message, message_input: Message, manager: DialogManager):
    await manager.switch_to(AdminSG)


async def export_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    if button.widget_id == "export_chats":
        groups_ids = await get_all_groups_with_bot_ids()
        group_ids = "\n".join(str(group_id) for group_id in groups_ids)
        await callback.message.answer_document(
            BufferedInputFile(io.BytesIO(group_ids.encode()).getbuffer(), "groups.txt")
        )
    elif button.widget_id == "export_users":
        users_ids = await get_all_users_with_pm_ids()
        user_ids = "\n".join(str(user_id) for user_id in users_ids)
        await callback.message.answer_document(
            BufferedInputFile(io.BytesIO(user_ids.encode()).getbuffer(), "users.txt")
        )
    await manager.switch_to(AdminSG.menu)


async def get_statistics(dialog_manager: DialogManager, **kwargs):
    created_users_today = await get_users_count_created_by_date(datetime.datetime.now().date())
    created_users_yesterday = await get_users_count_created_by_date(
        datetime.datetime.now().date() - datetime.timedelta(days=1)
    )
    last_active_users_today = await get_users_count_last_active_today()
    last_active_users_yesterday = await get_yesterday_users_active()
    groups_added_today = await get_groups_count_created_by_date(datetime.datetime.now().date())
    groups_added_yesterday = await get_groups_count_created_by_date(
        datetime.datetime.now().date() - datetime.timedelta(days=1)
    )
    last_active_groups_today = await get_groups_count_last_active_today()
    last_active_groups_yesterday = await get_yesterday_groups_active()

    total_users = await get_user_with_pm_count()
    total_active_groups = await get_group_with_bot_count()
    return {
        "created_users_today": created_users_today,
        "created_users_yesterday": created_users_yesterday,
        "last_active_users_today": last_active_users_today,
        "last_active_users_yesterday": last_active_users_yesterday,
        "groups_added_today": groups_added_today,
        "groups_added_yesterday": groups_added_yesterday,
        "last_active_groups_today": last_active_groups_today,
        "last_active_groups_yesterday": last_active_groups_yesterday,
        "total_users": total_users,
        "total_groups": total_active_groups
    }





admin_dialog = Dialog(
    Window(
        Const("Привет админ!"),
        Row(
            Start(Const("Рассылка"), id="mailing", state=MailingSG.choose_type),
            SwitchTo(Const("Статистика"), id="statistics", state=AdminSG.statistics),
        ),
        Row(
            Start(Const("Добавить админа"), id="add_admin", state=AddAdminSG.get_id),
            SwitchTo(Const("Ссылки"), id="links", state=AdminSG.choose_ref_action),
        ),
        Row(
            Start(Const("Создать промокод"), id="create_promo", state=CreatePromoSG.get_name),
            Start(Const("Удалить промокод"), id="delete_promo", state=DeletePromoSG.get_name),
        ),
        Start(Const("Сбросить сезон"), id="reset_season", state=DelSeasonSG.accept_del),

        state=AdminSG.menu,
    ),
    Window(
        Multi(
            Format("Сегодня:\n- ЛС: +{created_users_today}\n- Чаты: +{groups_added_today}"
                   "\n- Актив: 👤 {last_active_users_today} | 👥 {last_active_groups_today}"),
            Format("Вчера:\n- ЛС: +{created_users_yesterday}\n- Чаты: +{groups_added_yesterday}"
                   "\n- Актив: 👤 {last_active_users_yesterday} | 👥 {last_active_groups_yesterday}"),
            Format("За все время:\n- ЛС: {total_users}\n- Чаты: {total_groups}"),
            sep="\n\n"
        ),
        Next(Const("Экспорт")),
        Back(Const('Назад')),
        getter=get_statistics,
        state=AdminSG.statistics
    ),
    Window(
        Const("Выберите, что нужно экспортировать"),
        Button(Const("Чаты"), id="export_chats", on_click=export_clicked),
        Button(Const("Пользователи"), id="export_users", on_click=export_clicked),
        Back(Const('Назад')),
        state=AdminSG.export
    ),
    Window(
        Const("Управление ссылками"),
        Start(Const("Просмотр ссылок"), id="check_links", state=ViewRefLinkSG.link_list),
        Start(Const("Добавить ссылку"), id="add_link", state=AddRefLinkSG.get_link),
        Back(Const('Назад')),
        state=AdminSG.choose_ref_action
    ),
)
