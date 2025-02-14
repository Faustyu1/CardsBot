import os
import random
import sys

import aiogram
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.group import get_group, in_group_change, set_comments_active
from database.promo import get_promo, promo_use
from filters import CardFilter
from utils.kb import get_bonus_keyboard

sys.path.insert(0, sys.path[0] + "..")
import re
from datetime import datetime, timedelta
import emoji
import sqlalchemy
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated, InlineKeyboardButton, Message
from aiogram_dialog import DialogManager
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.text_decorations import markdown_decoration

sys.path.append(os.path.realpath('.'))
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER
from database.cards import get_all_cards
from database.models import Card
from database.user import add_card, add_coins, add_points, change_username, check_last_get, get_coins, get_luck, get_user, \
    in_pm_change, set_luck, update_last_get, is_nickname_taken, IsAlreadyResetException
from database.premium import check_premium
from middlewares import RegisterMiddleware
from filters.FloodWait import RateLimitFilter
from utils.loader import bot
from data.text import forbidden_symbols, settings_chat, name_card
import validators


text_triggers_router = Router()
text_triggers_router.my_chat_member.middleware(RegisterMiddleware())


@text_triggers_router.message(CardFilter(), RateLimitFilter(1.0))
async def komaru_cards_function(msg: Message, dialog_manager: DialogManager):
    user_id = msg.from_user.id
    user = await get_user(user_id)
    now = datetime.now()
    is_premium = await check_premium(user.premium_expire)
    if not await check_last_get(user.last_usage, is_premium):
        hours = 3 if is_premium else 4
        next_available = user.last_usage + timedelta(hours=hours)
        remaining = next_available - now
        
        hours_left = int(remaining.total_seconds() // 3600)
        minutes_left = int((remaining.total_seconds() % 3600) // 60)
        seconds_left = int(remaining.total_seconds() % 60)
        
        time_parts = []
        if hours_left > 0:
            time_parts.append(f"{hours_left} часов")
        if minutes_left > 0:
            time_parts.append(f"{minutes_left} минут")
        if seconds_left > 0:
            time_parts.append(f"{seconds_left} секунд")
        time_string = " ".join(time_parts)
        
        await msg.reply(
            "Осмотревшись, вы не нашли <b>Карту</b> поблизости 🤷‍♂️\n"
            f"⏳ Подождите <b>{time_string}</b>, чтобы попробовать снова", 
            parse_mode=ParseMode.HTML
        )
        return
    chosen_cat: Card = await random_cat(is_premium, user_id)
    description_text = f"\n📜 Описание: {chosen_cat.description}" if chosen_cat.description else ""

    if user.check_bonus_available():
        bonus_message = (
            "🎁 Получай <b>карточку</b> раз в 4 часа подписавшись на каналы спонсоров"
        )
        markup = await get_bonus_keyboard((await msg.bot.get_me()).username, msg.from_user.id)
    else:
        bonus_message = ""
        markup = None

    if chosen_cat.id in user.cards:
        coins = random.randint(2, 5)
        coins_db = await get_coins(user.telegram_id)
        await bot.send_photo(
            msg.chat.id,
            photo=chosen_cat.photo,
            caption=f"🌟 Карточка «<b>{chosen_cat.name}</b>» уже есть у вас"
                    f"\n\n💎 Редкость: <b>{chosen_cat.rarity}</b>\n "
                    f"✨ Очки: +<b>{chosen_cat.points}</b> [{user.points + int(chosen_cat.points)}]\n"
                    f"💰 Монеты • +{coins} [{coins_db + coins}]\n"
                    f"{description_text}\n\n"
                    f"{bonus_message}",
            reply_to_message_id=msg.message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=markup
        )
        await add_coins(user.telegram_id, int(coins), username=msg.from_user.username, in_pm=(msg.chat.type == "private"))
    else:
        coins = random.randint(5, 8)
        coins_db = await get_coins(user.telegram_id)
        await bot.send_photo(
            msg.chat.id,
            photo=chosen_cat.photo,
            caption=f"👻 Успех! Карточка «<b>{chosen_cat.name}</b>»"
                    f"\n\n💎 Редкость: <b>{chosen_cat.rarity}</b>\n "
                    f"✨ Очки: +<b>{chosen_cat.points}</b> [{user.points + int(chosen_cat.points)}]\n"
                    f"💰 Монеты • +{coins} [{coins_db + coins}]\n"
                    f"{description_text}\n"
                    f"{bonus_message}",
            reply_to_message_id=msg.message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=markup
        )
        await add_coins(user.telegram_id, int(coins), username=msg.from_user.username, in_pm=(msg.chat.type == "private"))
        await add_card(user.telegram_id, chosen_cat.id)

    await update_last_get(user.telegram_id)
    await add_points(user.telegram_id, int(chosen_cat.points))


@text_triggers_router.message(Command("name"))
@text_triggers_router.message(F.text.casefold().startswith("сменить ник".casefold()))
async def change_nickname(message: types.Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    user = await get_user(user_id)
    first_name = message.from_user.first_name
    premium_status = await check_premium(user.premium_expire)

    if message.text.startswith('/name'):
        command_parts = message.text.split(maxsplit=1)
        if len(command_parts) == 1: 
            await message.reply("Укажите новый никнейм после команды /name.")
            return
        new_nick = command_parts[1].strip()
    else:
        parts = message.text.casefold().split('сменить ник'.casefold(), 1)
        if len(parts) > 1 and parts[1].strip():
            new_nick = parts[1].strip()
        else:
            await message.reply("Никнейм не может быть пустым. Укажите значение после команды.")
            return

    if 5 > len(new_nick) or len(new_nick) > 32:
        await message.reply("Никнейм не должен быть короче 5 символов и длиннее 32 символов.")
        return

    if any(emoji.is_emoji(char) for char in new_nick):
        if not premium_status:
            await message.reply("Вы не можете использовать эмодзи в нике. Приобретите премиум в профиле!")
            return
    else:
        if not re.match(r'^[\w .,!?#$%^&*()-+=/\]+$|^[\w .,!?#$%^&*()-+=/а-яёА-ЯЁ]+$', new_nick):
            await message.reply("Никнейм может содержать только латинские/русские буквы, "
                              "цифры и базовые символы пунктуации.")
            return

    if '@' in new_nick or validators.url(new_nick) or 't.me' in new_nick:
        await message.reply("Никнейм не может содержать символ '@', ссылки или упоминания t.me.")
        return

    if await is_nickname_taken(new_nick):
        await message.reply("Никнейм занят")
        return

    try:
        await change_username(user.telegram_id, new_nick)
    except sqlalchemy.exc.IntegrityError as e:
        await message.reply("Никнейм занят")
        return
        
    await message.reply(f"Ваш никнейм был изменён на {new_nick}")


@text_triggers_router.message(F.text.casefold().startswith("промо".casefold()))
async def activate_promo(message: types.Message, dialog_manager: DialogManager):
    promocode = message.text.casefold().split('промо'.casefold(), 1)[1].strip()
    promo = await get_promo(promocode)
    if promo is None:
        await message.answer("Промокод не найден")
        return
    if promo.is_expiated_counts():
        await message.answer("Количество активаций промокода превышено.")
        return
    if promo.is_expiated_time():
        await message.answer("Промокод истек.")
        return
    try:
        channel_member = await message.bot.get_chat_member(promo.channel_id, message.from_user.id)
    except Exception:
        await message.answer("Возникла ошибки при проверке подписки на канал спонсора")
    if channel_member.status not in ["creator", "administrator", "member", "restricted"]:
        await message.answer("Вы не подписаны на канал спонсора, подпишитесь",
                             reply_markup=InlineKeyboardBuilder(
                                 InlineKeyboardButton(text="Канал спонсора", url=promo.link)
                             ).as_markup())
        return
    user = await get_user(message.from_user.id)
    if user.check_promo_expired(promocode):
        await message.answer("Вы уже использовали этот промокод")
        return
    try:
        await promo_use(user.telegram_id, promo)
        await message.answer("Промокод активирован успешно")
    except IsAlreadyResetException:
        await message.answer("Таймер уже на нуле, заберите карточку, а затем активируйте промокод.")


@text_triggers_router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_bot_added(update: ChatMemberUpdated):
    if update.chat.type == "private":
        await in_pm_change(update.from_user.id, True)
    elif update.chat.type in ["group", "supergroup"]:
        await in_group_change(update.chat.id, True)
        await update.answer(
            f"""👋 Добро пожаловать в мир Карточек!
    
🌟 Собирайте уникальные карточки и соревнуйтесь с другими игроками.
    
Как начать:
1. Напишите "{name_card}" для получения первой карточки.
2. Используйте команду /help для информации о доступных командах.
    
    Удачи в нашей вселенной!"""
        )


@text_triggers_router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_bot_deleted(update: ChatMemberUpdated):
    if update.chat.type == "private":
        await in_pm_change(update.from_user.id, False)
    elif update.chat.type in ["group", "supergroup"]:
        await in_group_change(update.chat.id, False)


def is_nickname_allowed(nickname):
    for symbol in forbidden_symbols:
        if re.search(re.escape(symbol), nickname, re.IGNORECASE):
            return False
    return True


async def random_cat(isPro: bool, user_id: int):
    cats = await get_all_cards()
    has_luck = await get_luck(user_id)

    if isPro:
        chances = {
            "Легендарная": 25,
            "Мифическая": 20,
            "Сверхредкая": 20,
            "Редкая": 35,
        }
    else:
        chances = {
            "Легендарная": 14,
            "Мифическая": 15,
            "Сверхредкая": 20,
            "Редкая": 51,
        }

    if has_luck:
        luck_bonus = 10
        chances["Легендарная"] += luck_bonus
        chances["Мифическая"] += luck_bonus
        chances["Сверхредкая"] += luck_bonus
        chances["Редкая"] += luck_bonus
        await set_luck(user_id, False)

    total = sum(chances.values())
    normalized_chances = {k: (v / total) * 100 for k, v in chances.items()}

    cumulative = 0
    ranges = {}
    for rarity, chance in normalized_chances.items():
        ranges[rarity] = (cumulative, cumulative + chance)
        cumulative += chance

    random_number = random.uniform(0, 100)

    for rarity, (start, end) in ranges.items():
        if start <= random_number < end:
            eligible_cats = [cat for cat in cats if cat.rarity == rarity]
            if eligible_cats:
                return random.choice(eligible_cats)

    rare_cats = [cat for cat in cats if cat.rarity == "Редкая"]
    if rare_cats:
        return random.choice(rare_cats)
    
    return 'чиво'


@text_triggers_router.message(Command("settings"))
async def settings(msg: types.Message, dialog_manager: DialogManager):
    settings = await get_group(int(msg.chat.id))
    status_text = "✅" if settings.comments_on else "❌"
    print(f"Settings from DB: {settings.comments_on}")
    builder = InlineKeyboardBuilder().add(
        InlineKeyboardButton(
            text=f"{status_text} Авто комментарии.",
            callback_data=f"settings:toogle:{msg.from_user.id}"
        ),
    )
    await msg.answer(settings_chat, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

@text_triggers_router.callback_query(F.data.startswith("settings:"))
async def settings_callback(callback: types.CallbackQuery):
    user_id = callback.data.split(":")[-1]
    if int(user_id) != callback.from_user.id:
        await callback.answer("Не ваша кнопка!", show_alert=True)
        return

    settings = await get_group(callback.message.chat.id)
    if settings:
        
        new_status = not settings.comments_on
        await set_comments_active(callback.message.chat.id, new_status)
        updated_settings = await get_group(callback.message.chat.id)
        status_text = "✅" if updated_settings.comments_on else "❌" 
        
        builder = InlineKeyboardBuilder().add(
            InlineKeyboardButton(
                text=f"{status_text} Авто комментарии.",
                callback_data=f"settings:toogle:{callback.from_user.id}"
            ),
        )
        
        try:
            await callback.message.edit_text(
                settings_chat,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        except aiogram.exceptions.TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await callback.answer()
            else:
                raise


@text_triggers_router.message()
async def on_any_message(msg: types.Message):
    pass