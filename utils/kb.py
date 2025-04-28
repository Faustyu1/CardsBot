import random

from aiogram import types
from aiogram.types import Message, LabeledPrice
from aiogram.utils.deep_linking import create_deep_link
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.bonus_link import create_bonus_link
from utils.states import user_button
from utils.loader import bot

async def start_kb(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="➡️ Добавить в группу",
        url="https://t.me/бот?startgroup=komaru&admin=change_info+restrict_members+"
            "delete_messages+pin_messages+invite_users"))
    return builder.as_markup()


async def help_kb(msg: Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔉 Наш канал", url="t.me/канал"))
    builder.row(types.InlineKeyboardButton(text="📝 Пользовательское соглашение",
                                           url="https://telegra.ph/Polzovatelskoe-soglashenie-08022025-02-08"))
    return builder.as_markup()


async def profile_kb(msg: Message):
    unique_id = str(random.randint(10000, 9999999999))
    user_button[unique_id] = str(msg.from_user.id)
    builder = InlineKeyboardBuilder()
    button_1 = types.InlineKeyboardButton(text="🃏 Мои карты", callback_data=f'show_cards_{unique_id}')
    button_3 = types.InlineKeyboardButton(text="💎 Премиум", callback_data=f'premium_callback_{unique_id}')
    builder.add(button_1, button_3)
    builder.adjust(2, 1)
    return builder.as_markup()


async def cards_kb(rarities):
    builder = InlineKeyboardBuilder()
    for rarity in rarities:
        callback_data = f'show_{rarity[:15]}'
        builder.add(types.InlineKeyboardButton(text=rarity, callback_data=callback_data))
    builder.adjust(1)
    return builder.as_markup()


async def get_card_navigation_keyboard(user_id, card_index, rarity, rarity_cards, card_id):
    builder = InlineKeyboardBuilder()
    love_button = types.InlineKeyboardButton(text="❤️", callback_data=f'love_just_{user_id}_{card_id}')
    builder.add(love_button)

    if card_index > 0:
        prev_button = types.InlineKeyboardButton(text="⬅️",
                                               callback_data=f'navigate_{user_id}_prev_{card_index - 1}_{rarity[:15]}')
        builder.add(prev_button)

    if card_index < len(rarity_cards) - 1:
        next_button = types.InlineKeyboardButton(text="➡️",
                                               callback_data=f'navigate_{user_id}_next_{card_index + 1}_{rarity[:15]}')
        builder.add(next_button)

    return builder.as_markup()


async def get_limited_card_navigation_keyboard(user_id, card_index, limited_cards, card_id):
    builder = InlineKeyboardBuilder()
    love_button = types.InlineKeyboardButton(text="❤️", callback_data=f'love_limited_{user_id}_{card_id}')
    builder.add(love_button)

    if card_index > 0:
        prev_button = types.InlineKeyboardButton(
            text="⬅️",
            callback_data=f'navigate_limited_{user_id}_prev_{card_index - 1}'
        )
        builder.add(prev_button)

    if card_index < len(limited_cards) - 1:
        next_button = types.InlineKeyboardButton(
            text="➡️",
            callback_data=f'navigate_limited_{user_id}_next_{card_index + 1}'
        )
        builder.add(next_button)

    return builder.as_markup()


async def top_kb(callback, choice):
    builder = InlineKeyboardBuilder()
    if choice == "all_top":
        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="🃏 Топ по карточкам",
                                              callback_data=f'top_cards_cards_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="💯 Топ по очкам",
                                              callback_data=f'top_cards_point_{unique_id}')
        button_3 = types.InlineKeyboardButton(text="⌛️ Топ за все время",
                                              callback_data=f'top_cards_all_{unique_id}')
        builder.add(button_1, button_2, button_3)
        return builder.as_markup()
    elif choice == "cards":
        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="💯 Топ по очкам",
                                              callback_data=f'top_cards_point_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="⌛️ Топ за все время",
                                              callback_data=f'top_cards_all_{unique_id}')
        builder.add(button_1, button_2)
        return builder.as_markup()
    elif choice == "point":

        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="🃏 Топ по карточкам",
                                              callback_data=f'top_cards_cards_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="⌛️ Топ за все время",
                                              callback_data=f'top_cards_all_{unique_id}')
        builder.add(button_1, button_2)
        return builder.as_markup()
    elif choice == "all":

        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(callback.from_user.id)
        button_1 = types.InlineKeyboardButton(text="🃏 Топ по карточкам",
                                              callback_data=f'top_cards_cards_{unique_id}')
        button_2 = types.InlineKeyboardButton(text="💯 Топ по очкам",
                                              callback_data=f'top_cards_point_{unique_id}')
        builder.add(button_1, button_2)
        return builder.as_markup()


async def premium_keyboard(unique_id):
    builder = InlineKeyboardBuilder()
    rub_button = types.InlineKeyboardButton(text="🏦 Оплатить картой", callback_data=f"pay_rub_{unique_id}")
    stars_button = types.InlineKeyboardButton(text="🌟 Оплатить звездами", callback_data=f"pay_stars_{unique_id}")
    builder.add(rub_button, stars_button)
    return builder.as_markup()


async def payment_keyboard(quantity):
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить {quantity} ⭐️", pay=True)

    return builder.as_markup()


async def payment_crypto_keyboard(invoice_id, invoice_url):
    builder = InlineKeyboardBuilder()
    pay_button = types.InlineKeyboardButton(text="Оплатить", url=invoice_url)
    paid_button = types.InlineKeyboardButton(text="Я оплатил",
                                             callback_data=f"verify_payment_{invoice_id}")
    builder.add(pay_button, paid_button)
    return builder.as_markup()


async def subscribe_keyboard():
    builder = InlineKeyboardBuilder()
    subscribe_button = types.InlineKeyboardButton(text="Подписаться", url="https://t.me/канал")
    builder.add(subscribe_button)
    return builder.as_markup()


async def get_bonus_keyboard(username: str, user_id: int):
    builder = InlineKeyboardBuilder()
    link_code = (await create_bonus_link(user_id)).code
    link = create_deep_link(username, "start", f"bonus_{link_code}")
    builder.button(text="Получить бонус", url=link)
    return builder.as_markup()


async def check_subscribe_keyboard(link: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="Проверить", callback_data=f"check_subscribe_{link}")
    return builder.as_markup()


async def shop_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="⚡️ Бустеры",
            callback_data="shop:boost"
        ),
        types.InlineKeyboardButton(
            text="💰 Монеты",
            callback_data="shop:coins"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


async def boost_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="☘️ Удача",
            callback_data="boost:luck"
        ),
        types.InlineKeyboardButton(
            text="⏳ Ускоритель времени",
            callback_data="boost:time"
        ),
        types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="shop:back"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


async def coins_keyboard():
    builder = InlineKeyboardBuilder()
    coin_values = [50, 100, 200, 300, 400, 500, 800, 1000, 1500, 2000]

    for i in range(0, len(coin_values), 2):
        row = []
        for j in range(2):
            if i + j < len(coin_values):
                value = coin_values[i + j]
                row.append(types.InlineKeyboardButton(text=f"💰 {value}", callback_data=f"shop:buy:{value}"))
        builder.row(*row)

    builder.row(types.InlineKeyboardButton(text="‹ Назад", callback_data="shop:back"))
    
    return builder.as_markup()


async def payment_boost_keyboard(quantity, msg, to_buy):
    invoice_link = await msg.bot.create_invoice_link(
        title="🌟 Покупка монет",
        description="Покупка монет",
        prices=[LabeledPrice(label="XTR", amount=quantity)],
        provider_token="",
        payload="boost:luck",
        currency="XTR"
    )
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Купить", callback_data=f"boost:buy:{to_buy}"))
    builder.add(types.InlineKeyboardButton(text="Назад", callback_data="shop:back"))
    builder.adjust(1)

    return builder.as_markup()