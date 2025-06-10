import logging
import random

from aiogram import F, Router, types
from aiogram.types import InputMediaPhoto, Message
from aiogram.utils.text_decorations import html_decoration
from aiogram.filters import Command
from aiogram_dialog import DialogManager
from sqlalchemy import func

from database.cards import get_all_cards, get_card, get_lcard
from database.models import Card, User
from database.premium import check_premium
from database.top import get_me_on_top, get_top_users_by_all_points, get_top_users_by_cards, get_top_users_by_points
from database.user import get_user, set_love_card
from filters import ProfileFilter
from handlers.premium import send_payment_method_selection
from utils.kb import cards_kb, get_card_navigation_keyboard, get_limited_card_navigation_keyboard, profile_kb, top_kb
from utils.loader import bot
from utils.states import get_dev_titul, get_titul, user_button
from data.text import responses
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.parse_mode import ParseMode

profile_router = Router()


async def send_initial_card_with_navigation(chat_id, user_id, rarity, rarity_cards, card_index):
    if card_index < len(rarity_cards):
        card: Card = rarity_cards[card_index]
        photo_data = card.photo
        caption = f"{card.name}\nРедкость: {card.rarity}\n\nОчки: {str(card.points)}\n"

        markup = await get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card.id)

        await bot.send_photo(chat_id, photo=photo_data, caption=caption, reply_markup=markup)
    else:
        logging.error(f"Card index {card_index} out of range for rarity cards")


async def send_card_with_navigation(chat_id, message_id, user_id, rarity, rarity_cards, card_index):
    if card_index < len(rarity_cards):
        card: Card = rarity_cards[card_index]
        photo_data = card.photo
        caption = f"{card.name}\nРедкость: {card.rarity}\n\nОчки: {str(card.points)}\n"

        markup = await get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card.id)

        media = InputMediaPhoto(media=photo_data)
        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id)
        await bot.edit_message_caption(caption=caption, chat_id=chat_id, message_id=message_id, reply_markup=markup)
    else:
        logging.error(f"Card index {card_index} out of range for rarity cards")


@profile_router.message(ProfileFilter() or F.command("profile"))
async def user_profile(msg: Message, dialog_manager: DialogManager):
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name
    last_name = msg.from_user.last_name or ""
    user = await get_user(user_id)
    titul = await get_titul(user.card_count)
    collected_cards = len(user.cards)
    total_cards = len(await get_all_cards())
    if user.love_card
        if user.love_card["is_limited"]:
            favorite_card = await get_lcard(user.love_card["id"])
        else:
            favorite_card = await get_card(user.love_card["id"])
    else:
        favorite_card = None

    favorite_card_name = html_decoration.bold(html_decoration.quote(favorite_card.name)) if favorite_card else "нету"
    premium_status = await check_premium(user.premium_expire)
    premium_message = f"Премиум: активен до {user.premium_expire.date()}" if premium_status else "<blockquote>Рекомендуем приобрести Premium</blockquote>"

    if user_id in [6184515646, 1268026433, 5493956779, 1022923020, 851455143, 6794926384, 6679727618]:
        dev_titul = await get_dev_titul(user_id)
        dev_titul_message = f"<blockquote> 🪬 Dev Титул: {dev_titul} </blockquote>"
    else:
        dev_titul_message = ""

    try:
        user_profile_photos = await bot.get_user_profile_photos(user_id, limit=1)
        if user_profile_photos.photos:
            photo = user_profile_photos.photos[0][-1]
            file_id = photo.file_id

            photo_cache = file_id
        else:
            photo_cache = 'https://tinypic.host/images/2025/02/14/cat.jpeg'

        caption = (
            f"Профиль «{html_decoration.bold(html_decoration.quote(user.nickname))}»\n\n"
            f"🔎 ID <b>• {user.id}</b>\n"
            f"🃏 Карт <b>• {collected_cards}</b> из <b>{total_cards}</b>\n"
            f"✨ Очки <b>• {user.points}</b>\n"
            f"💰 Монеты <b>• {user.coins}</b>\n"
            f"🏆 Титул <b>• {titul}</b>\n"
            f"❤️‍🔥 Любимая карточка <b>• {favorite_card_name}</b>\n"
            f"{premium_message}\n"
            f"{dev_titul_message}\n"
        )
        markup = await profile_kb(msg)

        await bot.send_photo(msg.chat.id, photo=photo_cache, caption=caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        if "bot was blocked by the user" in str(e):
            await msg.answer("Пожалуйста, разблокируйте бота для доступа к вашему профилю.")
        else:
            print(e)
            await msg.answer(
                "Произошла ошибка при доступе к вашему профилю. Попробуйте позже.")


@profile_router.message(ProfileFilter() or F.command("profile"))
async def user_profile_comments(msg: Message, dialog_manager: DialogManager):
    await msg.reply("Пожалуйста перейдите в чат для использования бота!")


@profile_router.callback_query(F.data.startswith("show_cards"))
async def show_cards_second(callback: types.CallbackQuery, dialog_manager: DialogManager):
    unique_id = str(callback.data.split('_')[-1])
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(text=random.choice(responses), show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    user_nickname = callback.from_user.first_name
    
    markup = InlineKeyboardBuilder()
    markup.row(types.InlineKeyboardButton(text="ОБЫЧНЫЕ КАРТОЧКИ", callback_data=f"show_usual_{unique_id}"))
    markup.row(types.InlineKeyboardButton(text="ЛИМИТИРОВАННЫЕ КАРТОЧКИ", callback_data=f"show_limited_{unique_id}"))
    
    try:
        await bot.send_message(user_id, "Выберите тип карточек:", reply_markup=markup.as_markup())
        if callback.message.chat.type in ["supergroup", "group"]:
            await bot.send_message(chat_id=callback.message.chat.id,
                                 text=f"{user_nickname}, выбор отправлен вам в личные сообщения!")
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение: {str(e)}")
        await callback.answer("Напишите боту что-то в личные сообщения!", show_alert=True)


@profile_router.callback_query(F.data.startswith("show_usual_"))
async def show_usual_cards(callback: types.CallbackQuery):
    unique_id = callback.data.split('_')[-1]
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(text=random.choice(responses), show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)

    if not user.cards:
        await callback.answer("У вас пока нет обычных карточек", show_alert=True)
        return

    rarities = set()
    for card_id in user.cards:
        card = await get_card(card_id)
        if card:
            rarities.add(card.rarity)

    builder = InlineKeyboardBuilder()
    for rarity in rarities:
        builder.row(types.InlineKeyboardButton(
            text=rarity,
            callback_data=f"usual_rarity_{rarity}_{unique_id}"
        ))

    await callback.message.edit_text(
        "Выберите редкость карточек:",
        reply_markup=builder.as_markup()
    )


@profile_router.callback_query(F.data.startswith("usual_rarity_"))
async def show_usual_cards_by_rarity(callback: types.CallbackQuery):
    _, _, rarity, unique_id = callback.data.split('_', 3)
    
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(text=random.choice(responses), show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)

    cards_of_rarity = []
    for card_id in user.cards:
        card = await get_card(card_id)
        if card and card.rarity == rarity:
            cards_of_rarity.append(card)

    if not cards_of_rarity:
        await callback.answer(f"У вас нет карточек редкости {rarity}", show_alert=True)
        return

    card = cards_of_rarity[0]
    keyboard = await get_card_navigation_keyboard(user_id, 0, rarity, cards_of_rarity, card.id)
    caption = (
        f"🃏 ОБЫЧНАЯ КАРТОЧКА\n"
        f"<b>{card.name}</b>\n"
        f"Редкость: {card.rarity}\n"
        f"Очки: {card.points}\n"
    )

    await bot.send_photo(
        callback.message.chat.id,
        photo=card.photo,
        caption=caption,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@profile_router.callback_query(F.data.startswith("show_limited_"))
async def show_limited_cards(callback: types.CallbackQuery, dialog_manager: DialogManager):
    unique_id = callback.data.split('_')[-1]
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(text=random.choice(responses), show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)

    if user.limited_cards:
        limited_cards = []
        for card_id in user.limited_cards:
            card = await get_lcard(card_id)
            if card:
                limited_cards.append(card)

        if limited_cards:
            card = limited_cards[0]
            keyboard = await get_limited_card_navigation_keyboard(user_id, 0, limited_cards, card.id)
            caption = (
                f"🎴 ЛИМИТИРОВАННАЯ КАРТОЧКА\n"
                f"<b>{card.name}</b>\n\n"
                f"💎 Цена: {card.price:,} монет\n"
                f"📦 Тираж: {card.buy_count}/{card.edition}\n"
            )
            if card.description:
                caption += f"\n{card.description}"

            await callback.message.edit_text("Ваши лимитированные карточки:")
            await bot.send_photo(
                callback.message.chat.id,
                photo=card.photo,
                caption=caption,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await callback.answer("Произошла ошибка при загрузке карточек", show_alert=True)
    else:
        await callback.answer("У вас пока нет лимитированных карточек", show_alert=True)


@profile_router.callback_query(F.data.startswith("navigate_limited_"))
async def navigate_limited_cards(callback: types.CallbackQuery):
    try:
        parts = callback.data.split('_')
        user_id = int(parts[2])
        direction = parts[3]
        new_index = int(parts[4])

        user = await get_user(user_id)
        limited_cards = []
        for card_id in user.limited_cards:
            card = await get_lcard(card_id)
            if card:
                limited_cards.append(card)

        if 0 <= new_index < len(limited_cards):
            card = limited_cards[new_index]
            keyboard = await get_limited_card_navigation_keyboard(user_id, new_index, limited_cards, card.id)
            
            caption = (
                f"🎴 ЛИМИТИРОВАННАЯ КАРТОЧКА\n"
                f"<b>{card.name}</b>\n\n"
                f"💎 Цена: {card.price:,} монет\n"
                f"📦 Тираж: {card.buy_count}/{card.edition}\n"
            )
            if card.description:
                caption += f"\n{card.description}"

            media = InputMediaPhoto(media=card.photo, caption=caption, parse_mode="HTML")
            await callback.message.edit_media(media=media, reply_markup=keyboard)
        else:
            await callback.answer("Карточка не найдена")
    except Exception as e:
        logging.error(f"Error in navigate_limited_cards: {str(e)}")
        await callback.answer("Произошла ошибка при навигации")
        

@profile_router.callback_query(F.data.startswith("navigate_"))
async def navigate_cards(callback: types.CallbackQuery):
    try:
        parts = callback.data.split('_')
        user_id = int(parts[1])
        direction = parts[2]
        new_index = int(parts[3])
        rarity = parts[4]

        user = await get_user(user_id)
        cards_of_rarity = []
        for card_id in user.cards:
            card = await get_card(card_id)
            if card and card.rarity == rarity:
                cards_of_rarity.append(card)

        if 0 <= new_index < len(cards_of_rarity):
            card = cards_of_rarity[new_index]
            keyboard = await get_card_navigation_keyboard(user_id, new_index, rarity, cards_of_rarity, card.id)
            
            caption = (
                f"🃏 ОБЫЧНАЯ КАРТОЧКА\n"
                f"<b>{card.name}</b>\n"
                f"Редкость: {card.rarity}\n"
                f"Очки: {card.points}\n"
            )

            media = InputMediaPhoto(media=card.photo, caption=caption, parse_mode="HTML")
            await callback.message.edit_media(media=media, reply_markup=keyboard)
        else:
            await callback.answer("Карточка не найдена")
    except Exception as e:
        logging.error(f"Error in navigate_cards: {str(e)}")
        await callback.answer("Произошла ошибка при навигации")


@profile_router.callback_query(F.data.startswith("love_"))
async def handle_love_card(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    card_type = parts[1]
    user_id = int(parts[2])
    card_id = int(parts[3])

    if card_type == "limited":
        card = await get_lcard(card_id)
        is_limited = True
    else:
        card = await get_card(card_id)
        is_limited = False
    if card is not None:
        await set_love_card(user_id, card_id, is_limited)
        await bot.answer_callback_query(callback.id, f"Карточка '{card.name}' теперь ваша любимая!")
    else:
        await bot.answer_callback_query(callback.id, "Не найдено карточек с таким ID.")


@profile_router.callback_query(F.data.startswith("top_komaru"))
async def top_komaru(callback: types.CallbackQuery):
    unique_id = str(callback.data.split('_')[-1])
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return
    markup = await top_kb(callback, "all_top")
    await callback.message.answer(
        text="Топ 10 пользователей по карточкам. Выберите кнопку:",
        reply_markup=markup)
    

@profile_router.message(Command("top"))
async def top_komaru_command(msg: Message):
    markup = await top_kb(msg, "all_top")
    await msg.answer("🏆 Топ 10 игроков:\n<blockquote> Выберите по какому значению показать топ</blockquote>", reply_markup=markup,parse_mode=ParseMode.HTML)



@profile_router.callback_query(F.data.startswith("top_cards_"))
async def cards_top_callback(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    choice = parts[2]
    unique_id = str(parts[-1])

    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return

    user_id = callback.from_user.id
    user = await get_user(user_id)
    message_text = ""

    if choice == "cards":
        top = await get_top_users_by_cards()
        user_rank = await get_me_on_top(func.cardinality(User.cards), user_id)

        message_text = "🃏 Топ 10 игроков по картам за сезон\n\n"
        for top_user in top:
            message_text += f"{top_user[0]}. {top_user[1]} {top_user[2]}: {top_user[3]} карточек"
            if user_id == 6184515646:
                message_text += f" (user_id: {top_user[4]})"
            message_text += "\n"

        if user_rank and user_rank > 10:
            message_text += (f"\n🎖️ Ваше место • {user_rank}"
                             f" ({user.nickname}: {len(user.cards)} карточек)")

        markup = await top_kb(callback, "cards")

    elif choice == "point":
        top = await get_top_users_by_points()
        user_rank = await get_me_on_top(User.points, user_id)

        message_text = "🍀 Топ 10 игроков по очкам за этот сезон\n\n"
        for top_user in top:
            message_text += f"{top_user[0]}. {top_user[1]} {top_user[2]}: {top_user[3]} очков\n"
        if user_rank and user_rank > 10:
            message_text += (f"\n🎖️ Ваше место • {user_rank} "
                             f"({user.nickname}: {user.points} очков)")

        markup = await top_kb(callback, "point")

    elif choice == "all":
        top = await get_top_users_by_all_points()
        user_rank = await get_me_on_top(User.all_points, user_id)

        message_text = "🌎 Топ 10 игроков по очкам за всё время\n\n"
        for top_user in top:
            message_text += f"{top_user[0]}. {top_user[1]} {top_user[2]}: {top_user[3]} очков\n"

        if user_rank and user_rank > 10:
            message_text += (f"\n🎖️ Ваше место • {user_rank} "
                             f"({user.nickname}: {user.all_points} очков)")

        markup = await top_kb(callback, "all")
    else:
        markup = await top_kb(callback, "all")

    if not message_text:
        message_text = "Не удалось получить данные. Попробуйте позже."

    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=message_text, reply_markup=markup)


@profile_router.callback_query(F.data.startswith("premium_callback"))
async def handler_premium(callback: types.CallbackQuery):
    unique_id = callback.data.split('_')[-1]
    if unique_id not in user_button or user_button[unique_id] != str(callback.from_user.id):
        await callback.answer(random.choice(responses), show_alert=True)
        return

    try:
        await send_payment_method_selection(callback, callback.from_user.id, unique_id)
        if callback.message.chat.type != "private":
            await callback.message.answer(
                f"{str(callback.from_user.first_name)}, "
                f"информация о способах оплаты отправлена вам в личные сообщения.")
    except Exception as e:
        print(e)
        await callback.answer("Пожалуйста, напишите боту что-то в личные сообщения, чтобы я смог отправить информацию.",
                              show_alert=True)
