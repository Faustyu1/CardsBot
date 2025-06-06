import random
import re
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from database.bonus_link import deactivate_bonus_link, delete_bonus_link, get_bonus_link
from database.cards import parse_cards, parse_limited_cards
from database.group import set_group_refer_code
from database.premium import check_premium
from database.ref_link import get_ref_link
from database.user import check_last_get, set_last_get
from database.user import (
    get_user,
    in_pm_change,
    set_user_refer_code,
    update_last_bonus_get,
)
from handlers.admin_dialogs.admin_states import AdminSG
from handlers.premium import send_payment_method_selection
from utils import loader
from utils.kb import check_subscribe_keyboard, help_kb, premium_keyboard, start_kb
from utils.loader import admins, flyer
from utils.states import user_button
from data.text import (
    HELP_MESSAGE,
    PREMIUM_TEXT,
    PRIVACY_MESSAGE,
    WELCOME_MESSAGE,
    WELCOME_MESSAGE_PRIVATE,
)

commands_router = Router()


@commands_router.message(
    CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r"bonus_(\w+)")))
)
async def handler_bot_start(msg: Message, command: CommandObject):
    link = await get_bonus_link(command.args.split("_")[-1])

    if link is None or not link.is_active:
        await msg.answer("Бонус не найден или уже использован")
        return

    user_id = link.for_user_id
    if user_id != msg.from_user.id:
        await msg.answer(
            "Это не ваш бонус. Напишите /bonus и перейдите по ссылке для получения бонуса"
        )
        return

    user = await get_user(msg.from_user.id)
    if user.check_bonus_available():
        is_subscribe = await flyer.check(msg.from_user.id, msg.from_user.language_code)
        if is_subscribe:
            if await check_last_get(
                user.last_usage, await check_premium(user.premium_expire)
            ):
                await msg.answer(
                    "У вас есть возможность получить карточку сейчас, используйте ее "
                    "и возвращайтесь за бонусом!"
                )
            else:
                await update_last_bonus_get(msg.from_user.id)
                await set_last_get(
                    user.telegram_id, datetime.now() - timedelta(hours=4)
                )

                await deactivate_bonus_link(link.code)

                await msg.answer("Бонус получен. Вы можете снова получить карточку")
        else:
            await msg.answer(
                "После подписки на каналы спонсоров нажмите чтобы получить бонус",
                reply_markup=await check_subscribe_keyboard(link.code),
            )
    else:
        await msg.answer("Упс... 12 часов с последнего бонуса не прошло")


@commands_router.message(Command("bonus"))
async def handler_bonus_command(msg: Message):
    if msg.chat.type != "private":
        await msg.answer("❗️ Данная команда работает только в ЛС")
        return
    user = await get_user(msg.from_user.id)

    if not user.check_bonus_available():
        await msg.answer("Упс... 4 часа с последнего бонуса не прошло")
        return

    is_subscribe = await flyer.check(msg.from_user.id, msg.from_user.language_code)
    if is_subscribe:
        if await check_last_get(
            user.last_usage, await check_premium(user.premium_expire)
        ):
            await msg.answer(
                "У вас есть возможность получить карточку сейчас, используйте ее "
                "и возвращайтесь за бонусом!"
            )
        else:
            await update_last_bonus_get(msg.from_user.id)
            await set_last_get(user.telegram_id, datetime.now() - timedelta(hours=4))
            await msg.answer("Бонус получен. Вы можете снова получить карточку")
    else:
        temp_code = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10)
        )
        await msg.answer(
            "После подписки на каналы спонсоров нажмите чтобы получить бонус",
            reply_markup=await check_subscribe_keyboard(temp_code),
        )


@commands_router.message(Command("premium"))
async def premium_command(msg: Message):
    try:
        unique_id = str(random.randint(10000, 9999999999))
        markup = await premium_keyboard(unique_id)
        await msg.bot.send_message(
            msg.from_user.id,
            f"{PREMIUM_TEXT} Выберите способ оплаты премиума:",
            reply_markup=markup,
            parse_mode="HTML",
        )
        if msg.chat.type != "private":
            await msg.answer(
                f"{str(msg.from_user.first_name)}, "
                f"информация о способах оплаты отправлена вам в личные сообщения."
            )
    except Exception as e:
        print(e)
        await msg.reply(
            "Пожалуйста, напишите боту что-то в личные сообщения, чтобы я смог отправить информацию."
        )


@commands_router.callback_query(F.data.startswith("check_subscribe_"))
async def check_subscribe(callback: CallbackQuery, dialog_manager: DialogManager):
    link_code = callback.data.split("_")[-1]
    link = await get_bonus_link(link_code)
    if link is None or not link.is_active:
        await callback.message.answer("Бонус не найден или уже использован")
        await callback.message.delete()
        return
    is_subscribe = await flyer.check(
        callback.from_user.id, callback.from_user.language_code
    )
    user = await get_user(callback.from_user.id)
    if is_subscribe:
        if await check_last_get(
            user.last_usage, await check_premium(user.premium_expire)
        ):
            await callback.message.answer(
                "У вас есть возможность получить карточку сейчас, используйте ее "
                "и возвращайтесь за бонусом!"
            )
        else:
            await update_last_bonus_get(callback.from_user.id)
            await delete_bonus_link(link_code)
            await set_last_get(user.telegram_id, datetime.now() - timedelta(hours=4))
            await callback.message.answer(
                "Бонус получен. Вы можете снова получить карточку"
            )
            await callback.message.delete()
        await callback.message.delete()
    else:
        await callback.answer("Подпишитесь что бы получить бонус")


@commands_router.message(
    CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r"ref_(\w+)")))
)
async def start_ref(msg: Message, command: CommandObject, created: bool):
    refer = command.args.split("_")[-1]
    ref_link = await get_ref_link(refer)
    await handler_start_command(msg, command)
    if ref_link is None:
        return
    if created and msg.chat.type == "private":
        await set_user_refer_code(msg.from_user.id, refer)
    elif created and msg.chat.type in ["group", "supergroup"]:
        await set_group_refer_code(msg.chat.id, refer)


@commands_router.message(CommandStart(deep_link=True, magic=F.args == "premium"))
async def start_premium(msg: Message, command: CommandObject):
    unique_id = str(random.randint(10000, 9999999999))
    user_button[unique_id] = str(msg.from_user.id)
    await send_payment_method_selection(msg, msg.from_user.id, unique_id)


@commands_router.message(CommandStart())
async def handler_start_command(msg: Message, command: CommandObject):
    if msg.chat.type == "private":
        user = await get_user(msg.from_user.id)
        if user.in_pm is None or user.in_pm is False:
            await in_pm_change(msg.from_user.id, True)
        markup = await start_kb(msg)
        await msg.answer(
            WELCOME_MESSAGE_PRIVATE, reply_markup=markup, parse_mode="HTML"
        )
    else:
        await msg.answer(WELCOME_MESSAGE, parse_mode="HTML")


@commands_router.message(Command("help"))
async def help_handler(msg: Message, dialog_manager: DialogManager):
    markup = await help_kb(msg)
    await msg.answer(HELP_MESSAGE, reply_markup=markup, parse_mode="HTML")


@commands_router.message(Command("privacy"))
async def privacy_handler(msg: Message, dialog_manager: DialogManager):
    markup = await help_kb(msg)
    await msg.answer(PRIVACY_MESSAGE, reply_markup=markup)


@commands_router.message(Command("admin"))
async def admin_cmd(message: Message, dialog_manager: DialogManager):
    if message.chat.type == "private":
        if message.from_user.id not in admins:
            return
        await dialog_manager.start(AdminSG.menu)


@commands_router.message(Command("test"))
async def test(msg: Message, dialog_manager: DialogManager):
    if msg.from_user.id not in loader.admins:
        return
    await msg.answer("Начинаю парс карточек...")
    await parse_cards("data/config.json")
    await parse_limited_cards("data/limited_config.json")
    await msg.answer("Карточки спаршены!")
