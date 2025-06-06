from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Next, Row
from aiogram_dialog.widgets.text import Const, Format

from database.user import clear_season
from handlers.admin_dialogs.admin_states import DelSeasonSG


async def accept_clicked(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    try:
        await callback.message.edit_text(
            "Очистка начата", reply_markup=InlineKeyboardBuilder().as_markup()
        )
        await clear_season()
        await manager.switch_to(DelSeasonSG.season_del)
    except Exception as e:
        manager.dialog_data["error"] = str(e)
        await manager.switch_to(DelSeasonSG.error)


season_delete_dialog = Dialog(
    Window(
        Const("Хотите сбросить сезон?"),
        Row(Cancel(Const("Нет")), Next(Const("Да"))),
        state=DelSeasonSG.accept_del,
    ),
    Window(
        Const("Точно???"),
        Row(
            Next(Const("Да")),
            Cancel(Const("Нет")),
        ),
        state=DelSeasonSG.accept_2,
    ),
    Window(
        Const('Что бы сбросить сезон нажмите на кнопку "Сбросить"'),
        Button(Const("Сбросить"), id="__reset__", on_click=accept_clicked),
        Cancel(Const("Отмена")),
        state=DelSeasonSG.accept_3,
    ),
    Window(
        Const("Сезон сброшен!"), Cancel(Const("В меню")), state=DelSeasonSG.season_del
    ),
    Window(
        Format("Ошибка: {dialog_data[error]}"),
        Cancel(Const("В меню")),
        state=DelSeasonSG.error,
    ),
)
