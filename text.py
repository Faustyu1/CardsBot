WELCOME_MESSAGE_PRIVATE = '''👋 Добро пожаловать в бота Komaru Cards!\n\n🌟 Собирайте уникальные карточки Комару и 
соревнуйтесь с другими игроками.\n\nЧтобы начать получать карточки напиши "<code>Комару</code>."\n\nИспользуйте 
команду /help для получения дополнительных команд.\n➡️ Нажмите кнопку ниже, чтобы добавить бота в группу:'''

WELCOME_MESSAGE = '''👋 Добро пожаловать в мир Комару!\n\n🌟 Собирайте уникальные карточки Комару и соревнуйтесь с 
другими игроками.\n\nКак начать:\n\n1. Напишите "Комару" для получения первой карточки.\n2. Используйте команду /help 
для информации о доступных командах.\n\nУдачи в нашей вселенной!'''

HELP_MESSAGE = (
    "<b>Komaru Cards</b> - Ваш путь во вселенную карточек комару.\n\n"
    "<b>Доступные команды:</b>\n\n"
    "<b>/start</b> - Начать работу с ботом\n"
    "<b>/help</b> - Получить помощь\n"
    "<b>профиль, комару профиль, кпрофиль</b> - Посмотреть свой профиль\n"
    "<b>сменить ник &lt;ник&gt;</b> - Смена ника в профиле\n"
    "<b>комару, получить карту, камар</b> - Искать котов и собирать карточки\n\n"
    "Удачи в нашей вселенной! Заметка: Пожалуйста выдайте боту админку для корректной работы."
)

PRIVACY_MESSAGE = '''Мы обрабатываем данные пользователей строго в целях улучшения функционала нашего бота. 
Гарантируем, что данные пользователя, включая идентификатор пользователя (user ID) и имя (first name), 
не будут переданы третьим лицам или использованы вне контекста улучшения бота. Наш приоритет — обеспечение 
безопасности и конфиденциальности информации, которую вы нам доверяете.\n\nДля повышения прозрачности нашей работы, 
мы также обязуемся предоставлять пользователю доступ к информации о том, какие данные собраны и как они используются. 
В случае изменения политики использования данных, мы своевременно информируем пользователей через обновления нашего 
пользовательского соглашения. Мы прилагаем все усилия, чтобы наш сервис был максимально безопасным и удобным для 
пользователя.'''

responses = [
    "Уберите лапки от чужой кнопки.",
    "Лапки вверх, вы арестованы!",
    "Ваши лапки не для этой кнопки.",
    "Лапки прочь от этой кнопки!",
    "Ваши лапки здесь лишние.",
    "Лапки прочь, нарушитель!",
    "Ваши лапки ошиблись кнопкой.",
    "Ваши лапки попали не туда.",
    "Лапки в сторону!",
    "Ваши лапки слишком любопытны!",
    "Лапки в сторону, эта кнопка охраняется."
]

PREMIUM_TEXT = (f"🔓 Что даст тебе Комару премиум?\n\n"
                f"⌛️ Возможность получать карточки каждые 3 часа вместо 4\n"
                f"🃏 Повышенная вероятность выпадения легендарных и мифических карт\n"
                f"🌐 Возможность использовать смайлики в никнейме\n"
                f"💎 Отображение алмаза в топе карточек\n"
                f"🔄 Более быстрая обработка твоих сообщений\n"
                f"🗓️ Срок действия 30 дней\n\n")

forbidden_symbols = [
    "\u5350",  # 卐 (нацистская свастика)
    "\u5351",  # 卑 (также используется как свастика)
    "\u534d",
    "1488",  
    "heil", 
    "hitler"
]
