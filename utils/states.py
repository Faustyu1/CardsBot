user_button = {}


async def get_dev_titul(user_id: int) -> str:
    if user_id == 40777:
        return "test"
    else:
        return "test"


async def get_titul(card_count):
    if card_count > 500:
        return "Мастер карточек"
    elif card_count > 250:
        return "Коллекционер"
    elif card_count > 150:
        return 'Эксперт карточек'
    elif card_count > 100:
        return 'Продвинутый коллекционер'
    elif card_count > 50:
        return f'Любитель'
    elif card_count > 20:
        return 'Начинающий коллекционер'
    else:
        return 'Новичок'
