from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.payment import PaymentService
import os
import uuid

router = Router()
payment_service = PaymentService()

class PaymentStates(StatesGroup):
    waiting_for_payment_type = State()
    waiting_for_payment_confirmation = State()

@router.message(Command("premium"))
async def cmd_premium(message: Message, state: FSMContext):
    premium_price = float(os.getenv('PREMIUM_PRICE', '299'))
    await message.answer(
        "🚀 <b>Premium</b>\n\n"
        "⏳ Возможность получать карточки каждые 3 часа вместо 4\n"
        "✨ Повышенная вероятность выпадения легендарных и мифических карт\n"
        "🔥 Возможность использовать смайлики в никнейме\n"
        "💎 Отображение алмаза в топе карточек\n"
        "⚡ Более быстрая обработка твоих сообщений\n"
        "Срок действия • 30 дней\n\n"
        f"<b>Выберите способ оплаты премиума:</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Telegram Stars", callback_data="pay_stars"),
                    InlineKeyboardButton(text="CryptoBot", callback_data="pay_crypto"),
                ],
                [
                    InlineKeyboardButton(text=f"Оплата картой ({premium_price}₽)", callback_data="buy_premium_rub"),
                ]
            ]
        ),
        parse_mode="HTML"
    )
    await state.set_state(PaymentStates.waiting_for_payment_confirmation)

@router.message(Command("coins"))
async def cmd_coins(message: Message, state: FSMContext):
    coins_price = float(os.getenv('COINS_PRICE', '99'))
    await message.answer(
        f"🪙 Покупка монет\n\n"
        f"Стоимость: {coins_price} ₽\n"
        f"Количество: 100 монет\n\n"
        f"Хотите приобрести монеты?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Купить", callback_data="buy_coins"),
                    InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")
                ]
            ]
        )
    )
    await state.set_state(PaymentStates.waiting_for_payment_confirmation)

@router.callback_query(F.data.startswith("buy_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    payment_type = callback.data.split("_")[1]
    order_id = str(uuid.uuid4())
    
    if payment_type == "premium":
        amount = float(os.getenv('PREMIUM_PRICE', '299'))
        description = "Премиум подписка на 30 дней"
    else:
        amount = float(os.getenv('COINS_PRICE', '99'))
        description = "Покупка 100 монет"
    
    payment_link = await payment_service.create_payment_link(
        amount=amount,
        description=description,
        order_id=order_id,
        success_url=f"https://t.me/{callback.message.chat.username}?start=payment_success_{order_id}",
        fail_url=f"https://t.me/{callback.message.chat.username}?start=payment_fail_{order_id}"
    )
    
    if payment_link:
        await callback.message.answer(
            f"Для оплаты перейдите по ссылке:\n{payment_link}\n\n"
            f"После успешной оплаты вы получите уведомление.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_payment_{order_id}"),
                        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")
                    ]
                ]
            )
        )
    else:
        await callback.message.answer("Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже.")
    
    await state.clear()

@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment(callback: CallbackQuery):
    order_id = callback.data.split("_")[2]
    payment_status = await payment_service.check_payment_status(order_id)
    
    if payment_status and payment_status.get('status') == 'SUCCESS':
        # Здесь нужно добавить логику начисления премиума или монет
        await callback.message.answer("✅ Оплата успешно подтверждена! Спасибо за покупку!")
    else:
        await callback.message.answer("❌ Оплата не подтверждена. Пожалуйста, попробуйте позже или обратитесь в поддержку.")

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Платеж отменен.")
    await state.clear()

@router.callback_query(F.data == "buy_premium_rub")
async def process_rub_payment(callback: CallbackQuery, state: FSMContext):
    order_id = str(uuid.uuid4())
    amount = float(os.getenv('PREMIUM_PRICE', '299'))
    description = "Премиум подписка на 30 дней"
    payment_link = await payment_service.create_payment_link(
        amount=amount,
        description=description,
        order_id=order_id,
        success_url=f"https://t.me/{callback.message.chat.username}?start=payment_success_{order_id}",
        fail_url=f"https://t.me/{callback.message.chat.username}?start=payment_fail_{order_id}"
    )
    if payment_link:
        await callback.message.answer(
            f"Для оплаты премиума перейдите по ссылке:\n{payment_link}\n\n"
            f"После успешной оплаты вы получите уведомление.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_payment_{order_id}"),
                        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")
                    ]
                ]
            )
        )
    else:
        await callback.message.answer("Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже.")
    await state.clear() 