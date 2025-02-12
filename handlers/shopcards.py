from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from database.cards import get_all_lcards, get_lcard, increment_buy_count
from database.user import add_coins, add_limited_card_to_user, check_user_has_limited_card, get_coins

shop_cards_router = Router()

async def get_card_text(card):
   text = (
       f"🎴 <b>{card.name}</b>\n\n"
       f"💎 Цена: {card.price:,} монет\n"
       f"📦 Тираж: {card.buy_count}/{card.edition}\n"
   )
   if card.description:
       text += f"\nℹ️ Описание: {card.description}"
   
   if card.buy_count >= card.edition:
       text += "\n\n❌ ТОВАР РАСПРОДАН"
   return text

def make_card_keyboard(card_id: int, total_cards: int):
    builder = InlineKeyboardBuilder()
    
    nav_buttons = []
    if card_id > 1:
        nav_buttons.append(types.InlineKeyboardButton(text="⬅️", callback_data=f"market:prev:{card_id}"))
    if card_id < total_cards:
        nav_buttons.append(types.InlineKeyboardButton(text="➡️", callback_data=f"market:next:{card_id}"))
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(types.InlineKeyboardButton(text="Купить 💎", callback_data=f"market:buy:{card_id}"))
    
    return builder.as_markup()


async def sort_cards_by_availability(cards):
   available = []
   sold_out = []
   for card in cards:
       if card.buy_count >= card.edition:
           sold_out.append(card)
       else:
           available.append(card)
   return available + sold_out


@shop_cards_router.message(Command("market"))
async def show_market_menu(message: types.Message):
   if message.chat.type != "private":
       await message.answer(
           "❌ Магазин доступен только в личных сообщениях!"
       )
       return

   builder = InlineKeyboardBuilder()
   builder.row(types.InlineKeyboardButton(
       text="ОТКРЫТЬ",
       callback_data="market:open"
   ))

   await message.answer(
       "🏪 Биржа лимитированных карточек",
       reply_markup=builder.as_markup()
   )
   

async def get_available_cards():
    all_cards = await get_all_lcards()
    return [card for card in all_cards if card.buy_count < card.edition]


@shop_cards_router.callback_query(F.data == "market:open")
async def open_market(callback: types.CallbackQuery):
   available_cards = await get_available_cards()
   if not available_cards:
       await callback.message.edit_text("В магазине нет доступных карточек")
       return
   
   first_card = available_cards[0]
   keyboard = make_card_keyboard(1, len(available_cards))
   
   await callback.message.delete()
   await callback.message.answer_photo(
       photo=first_card.photo,
       caption=await get_card_text(first_card),
       reply_markup=keyboard,
       parse_mode=ParseMode.HTML
   )
   await callback.answer()

@shop_cards_router.callback_query(F.data.startswith("market:"))
async def process_shop_callbacks(callback: types.CallbackQuery):
    action, current_pos = callback.data.split(":")[1:]
    current_pos = int(current_pos)
    available_cards = [card for card in await get_all_lcards() if card.buy_count < card.edition]
    
    if action in ["prev", "next"]:
        new_pos = current_pos - 1 if action == "prev" else current_pos + 1
        card = available_cards[new_pos - 1]
        
        keyboard = make_card_keyboard(new_pos, len(available_cards))
        
        await callback.message.edit_media(
            types.InputMediaPhoto(
                media=card.photo,
                caption=await get_card_text(card),
                parse_mode=ParseMode.HTML
            ),
            reply_markup=keyboard
        )
    
    elif action == "buy":
        card = available_cards[current_pos - 1]
        
        if await check_user_has_limited_card(callback.from_user.id, card.id):
            await callback.answer("У вас уже есть эта карточка!", show_alert=True)
            return
            
        user_coins = await get_coins(callback.from_user.id)
        if user_coins < card.price:
            await callback.answer(f"Недостаточно монет! Нужно: {card.price:,}", show_alert=True)
            return
            
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(text="Подтвердить ✅", callback_data=f"market:confirm:{card.id}"),
            types.InlineKeyboardButton(text="Отменить ❌", callback_data=f"market:cancel:{current_pos}")
        )
        
        await callback.message.answer(
            f"Купить карточку <b>{card.name}</b> за {card.price:,} монет?\nУ вас: {user_coins:,} монет",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    
    elif action == "confirm":
        card = await get_lcard(int(current_pos))
        
        if await check_user_has_limited_card(callback.from_user.id, card.id):
            await callback.answer("У вас уже есть эта карточка!", show_alert=True)
            return
            
        user_coins = await get_coins(callback.from_user.id)
        if user_coins < card.price:
            await callback.answer(f"Недостаточно монет! Нужно: {card.price:,}", show_alert=True)
            return
            
        await add_coins(callback.from_user.id, -card.price, callback.from_user.username, True)
        await increment_buy_count(card.id)
        await add_limited_card_to_user(callback.from_user.id, card.id)
        
        await callback.message.edit_text(
            f"Вы приобрели карточку <b>{card.name}</b>!\nПотрачено: {card.price:,} монет",
            parse_mode=ParseMode.HTML
        )
    
    elif action == "cancel":
        await callback.message.delete()
    
    await callback.answer()