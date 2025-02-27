import asyncio
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

from data.text import shop_text, booster_text, coins_text, confirmation_payment_text, luck_message, buy_luck_message, time_booster, dice_game, dice_limit
from utils.kb import shop_keyboard, boost_keyboard, coins_keyboard, payment_keyboard, payment_boost_keyboard
from database.user import add_coins, add_dice_get, get_coins, set_luck, get_luck, get_user, set_last_get, check_last_get
from datetime import datetime, timedelta
from utils.loader import bot


shop_router = Router()
@shop_router.message(Command("shop"))
async def shop(msg: Message):
    if msg.chat.type in ["group", "supergroup", "channel"]:
        await msg.reply("❗️ Данная команда работает только в ЛС")
        return
    await msg.answer(
        text=shop_text,
        reply_markup=await shop_keyboard(),
        parse_mode="HTML"
    )
    

@shop_router.callback_query(F.data.startswith("shop:"))
async def shop_callback(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    data = callback.data.split(":")
    if action == "boost":
        await callback.message.edit_text(
            text=booster_text,
            reply_markup=await boost_keyboard(),
            parse_mode="HTML"
        )
    elif action == "coins":
        await callback.message.edit_text(
            text=coins_text,
            reply_markup=await coins_keyboard(),
            parse_mode="HTML"
        )
    elif action == "back":
        await callback.message.edit_text(
            text=shop_text,
            reply_markup=await shop_keyboard(),
            parse_mode="HTML"
        )
    elif action == "buy":
        quantity = int(data[2])
        cost = int(quantity * 7 / 50)
        prices = [LabeledPrice(label="XTR", amount=cost)]
        await callback.message.answer_invoice(
            title="🌟 Покупка монет",
            description="Покупка монет",
            prices=prices,
            provider_token="",
            payload=f"coins:{quantity}",
            currency="XTR", 
            reply_markup=await payment_keyboard(cost),
        )

@shop_router.callback_query(F.data.startswith("boost:"))
async def boost_callback(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    if action == "luck":
        await callback.message.edit_text(
            text=luck_message,
            reply_markup=await payment_boost_keyboard(4, callback.message, "luck"),
            parse_mode="HTML"
        )
    elif action == "time":
        await callback.message.edit_text(
            text=time_booster,
            reply_markup=await payment_boost_keyboard(3, callback.message, "time"),
            parse_mode="HTML"
        )
    if action == "buy":
        to_buy = callback.data.split(":")[2]
        if to_buy == "luck":
            luck = await get_luck(callback.from_user.id)
            if luck:
                await callback.answer("У вас уже есть бустер!")
                return
            coins = await get_coins(callback.from_user.id)
            if coins < 20:
                await callback.answer("У вас недостаточно монет!")
                return
            await add_coins(callback.from_user.id, -20)
            await callback.message.answer(buy_luck_message)
            await set_luck(callback.from_user.id, True)
        elif to_buy == "time":
            coins = await get_coins(callback.from_user.id)
            if coins < 15:
                await callback.answer("У вас недостаточно монет!")
                return

            await add_coins(callback.from_user.id, -15)
            
            user = await get_user(callback.from_user.id)
            
            if user and user.last_usage:
                can_get_now = await check_last_get(user.last_usage, is_premium=False)
                if can_get_now:
                    await callback.answer("Вы уже можете получить карточку!")
                    return
                else:
                    new_time = user.last_usage - timedelta(hours=1)
                    await set_last_get(callback.from_user.id, new_time)
                    await callback.message.answer("Вы получили бустер на 1 час! Время ожидания сокращено.")
            else:
                await callback.answer("Вы уже можете получить карточку!")

@shop_router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)

@shop_router.message(F.successful_payment, lambda message: message.successful_payment.invoice_payload.startswith("coins"))
async def handle_coins_payment(message: Message):
    successful_payment = message.successful_payment
    invoice_payload = successful_payment.invoice_payload
    
    try:
        quantity_str = invoice_payload.split(":")[1]
        quantity = int(quantity_str)
    except Exception as e:
        await message.answer("Ошибка обработки платежа: неверный формат payload. Обратитесь в поддержку")
        return

    result = await add_coins(message.from_user.id, quantity, username=message.from_user.username, in_pm=True)
    
    if result:
        builder = InlineKeyboardBuilder().add(
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="shop:back"
            ))
        confirmation_text = confirmation_payment_text.replace("{quantity}", str(quantity))
        await message.answer(text=confirmation_text, parse_mode="HTML", reply_markup=builder.as_markup())
    else:
        await message.answer("Ошибка при добавлении монет. Попробуйте повторить позже.")

@shop_router.message(Command("diceplay"))
async def diceplay(msg: Message):
    user = await get_user(msg.from_user.id)
    if user and user.last_dice_play:
        time_since_last_throw = datetime.now() - user.last_dice_play
        cooldown = timedelta(minutes=7)
        if time_since_last_throw < cooldown:
            remaining_time = (cooldown - time_since_last_throw).total_seconds() // 60  # Учитываем всё время
            await msg.reply(text=dice_limit.format(int(remaining_time)), parse_mode="HTML")
            return
    dice = await msg.bot.send_dice(
        chat_id=msg.chat.id,
        reply_to_message_id=msg.message_id,
    )
    dice_value = dice.dice.value
    await asyncio.sleep(3)
    await add_coins(
        msg.from_user.id, 
        dice_value, 
        msg.from_user.username, 
        in_pm=(msg.chat.type == "private")
    )
    await add_dice_get(msg.from_user.id)

    await msg.reply(
        text=dice_game.format(dice_value, dice_value),
        parse_mode="HTML"
    )
