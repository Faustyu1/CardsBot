user_button = {}


async def get_dev_titul(user_id: int) -> str:
    if user_id == 5493956779:
        return "люпими квт рофл"
    elif user_id == 1022923020:
        return "@NAIX_EXE НУ ЧЕ ТАМ? BY @DERADERADERA."
    elif user_id in [1268026433, 6184515646]:
        return "Создатель"
    elif user_id == 851455143:
        return "несоня"
    elif user_id == 6794926384:
        return "ВАНМАРУ САМЫЙ ЛУЧШИЙ И АХУЕННЫЙ"
    elif user_id == 6679727618:
        return "Кошко юне"
    else:
        return "как ты вообще сюда попал?"


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
        return f'Любитель {name_card_rod_padezh}'
    elif card_count > 20:
        return 'Начинающий коллекционер'
    else:
        return 'Новичок'
