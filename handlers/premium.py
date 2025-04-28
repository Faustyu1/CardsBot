import logging
import random
from datetime import timedelta

from aiogram import F, Router, types
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from aiogram_dialog import DialogManager
from aiogram.utils.text_decorations import html_decoration
from aiogram.enums.parse_mode import ParseMode
from database.premium import add_premium
from utils.kb import payment_crypto_keyboard, payment_keyboard, premium_keyboard
from utils.loader import crypto
from utils.states import user_button
from data.text import PREMIUM_TEXT, responses
from utils.payment import PaymentService
import os
import uuid

premium_router = Router()


async def send_payment_method_selection(callback, user_id, unique_id):
    markup = await premium_keyboard(unique_id)
    await callback.bot.send_message(user_id, f"{PREMIUM_TEXT} Выберите способ оплаты премиума:",
                                 reply_markup=markup,parse_mode=ParseMode.HTML)   


@premium_router.callback_query(F.data.startswith("pay_stars_"))
async def pay_with_stars(callback: CallbackQuery, dialog_manager: DialogManager):
    try:
        prices = [LabeledPrice(label="XTR", amount=35)]
        await callback.message.answer_invoice(
            title="🌟 Premium",
            description="Покупка премиума!",
            prices=prices,
            provider_token="",
            payload="komaru_premium",
            currency="XTR",
            reply_markup=await payment_keyboard(35),
        )
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {str(e)}")
        logging.error(f"Error in pay_with_stars: {e}")


@premium_router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)


@premium_router.message(F.successful_payment, lambda message: message.successful_payment.invoice_payload == "komaru_premium")
async def handle_komaru_premium(message: types.Message):
    successful_payment = message.successful_payment
    await add_premium(message.from_user.id, timedelta(days=30))
    await message.answer("🌟 Спасибо за покупку Премиума! Наслаждайтесь эксклюзивными преимуществами.")
        


@premium_router.callback_query(F.data.startswith("pay_crypto_"))
async def create_and_send_invoice(callback: CallbackQuery, dialog_manager: DialogManager):
    try:
        invoice = await crypto.create_invoice(asset='USDT', amount=0.7)
        if not invoice:
            response = "Ошибка при создании инвойса. Попробуйте позже."
            await callback.bot.send_message(callback.from_user.id, response)
            return None

        markup = await payment_crypto_keyboard(invoice.invoice_id, invoice.bot_invoice_url)

        response = (
            f"Премиум активируется после подтверждения оплаты. Реквизиты: {invoice.bot_invoice_url}\n\nЦена: 0.70 USDT"
        )
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await callback.bot.send_message(callback.from_user.id, response, reply_markup=markup)
        return invoice
    except Exception as e:
        error_message = f"Ошибка при создании инвойса: {e}"
        await callback.bot.send_message(callback.from_user.id, error_message)
        return None


@premium_router.callback_query(F.data.startswith("verify_payment"))
async def verify_payment(call, dialog_manager: DialogManager):
    # Не обрабатываем Wata.pro (rub) здесь
    if call.data.startswith("verify_payment_rub_"):
        return
    parts = call.data.split('_')
    if len(parts) < 3:
        await call.bot.send_message(call.message.chat.id, "Ошибка в данных платежа.")
        return

    action, context, invoice = parts[0], parts[1], parts[2]

    try:
        print("Invoice ID:", invoice)
        payment_status = await get_invoice_status(invoice)
        if payment_status == 'paid':
            await add_premium(call.from_user.id, timedelta(days=30))
            await call.bot.send_message(call.from_user.id,
                                        "🌟 Спасибо за покупку Премиума! Наслаждайтесь эксклюзивными преимуществами.")
            await call.bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            await call.bot.send_message(call.from_user.id, "Оплата не прошла! Попробуйте еще раз.")
    except Exception as e:
        await call.bot.send_message(call.from_user.id, f"Произошла ошибка при проверке статуса платежа: {str(e)}")


async def get_invoice_status(invoice_id):
    try:
        invoice = await crypto.get_invoices(invoice_ids=int(invoice_id))
        return invoice.status
    except Exception as e:
        print(f"Ошибка при получении данных инвойса: {e}")
        return None


@premium_router.callback_query(F.data.startswith("pay_rub_"))
async def pay_with_rub(callback: CallbackQuery, dialog_manager: DialogManager):
    await callback.answer()
    payment_service = PaymentService()
    order_id = str(uuid.uuid4())
    amount = float(os.getenv('PREMIUM_PRICE', '299'))
    description = "Премиум подписка на 30 дней"
    payment_link = await payment_service.create_payment_link(
        amount=amount,
        description=description,
        order_id=order_id,
        success_url=f"https://t.me/ВАШ_ЮЗЕРНЕЙМ_БОТА?start=payment_success_{order_id}",
        fail_url=f"https://t.me/ВАШ_ЮЗЕРНЕЙМ_БОТА?start=payment_fail_{order_id}"
    )
    if payment_link:
        await callback.bot.send_message(
            callback.from_user.id,
            f"Для оплаты премиума перейдите по ссылке:\n{payment_link}\n\n"
            f"После успешной оплаты вы получите уведомление.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"verify_payment_rub_{order_id}"),
                        types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")
                    ]
                ]
            )
        )
    else:
        await callback.bot.send_message(callback.from_user.id, "Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже.")
    try:
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    except Exception:
        pass


@premium_router.callback_query(F.data.startswith("verify_payment_rub_"))
async def verify_payment_rub(callback: CallbackQuery, dialog_manager: DialogManager):
    print("DEBUG: verify_payment_rub triggered", callback.data)
    payment_service = PaymentService()
    order_id = callback.data.split("_")[-1]
    payment_status = await payment_service.check_payment_status(order_id)
    if payment_status and payment_status.get('status') == 'SUCCESS':
        await add_premium(callback.from_user.id, timedelta(days=30))
        await callback.message.answer("🌟 Спасибо за покупку Премиума! Наслаждайтесь эксклюзивными преимуществами.")
        try:
            await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except Exception:
            pass
    elif payment_status and payment_status.get('status') == 'OPENED':
        await callback.message.answer("❌ Оплата не подтверждена. Платёж ещё не завершён. Пожалуйста, попробуйте позже или обратитесь в поддержку.")
    else:
        await callback.message.answer("❌ Оплата не подтверждена. Пожалуйста, попробуйте позже или обратитесь в поддержку.")


@premium_router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, dialog_manager: DialogManager = None):
    # Пытаемся закрыть ссылку, если order_id есть в сообщении
    import re
    from utils.payment import PaymentService
    payment_service = PaymentService()
    # Пытаемся найти order_id в callback.message.reply_markup
    order_id = None
    if callback.message.reply_markup:
        for row in callback.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("verify_payment_rub_"):
                    order_id = btn.callback_data.split("_")[-1]
    if order_id:
        # Закрываем ссылку через Wata.pro
        await payment_service.close_payment_link(order_id)
    await callback.answer()
    try:
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
    except Exception:
        pass
    await callback.bot.send_message(callback.from_user.id, "Платёж был отменён.")
