# CardsBot for funny in Telegram

## Запуск бота

2. docker-compose up --build
3. docker-compose up
4. заполнить файл .env
```.env
BOT_TOKEN=1234343:AABBCCEE
ADMIN_IDS=77000,77001
CRYPTO_TOKEN=1234343:AABBOOCCEE
FLYER_TOKEN=FL-lekLE-lekLE-lekLE-lekLE

# Database Configuration
DB_DRIVER=postgresql+asyncpg
DB_HOST=ip
DB_PORT=5432
DB_NAME=folt_copy
DB_USER=user
DB_PASSWORD="password"
```
5. Чтобы остановить контейнер пропишите docker-compose stop


## Файлы для заполнения
1. data/config.json
2. data/text.py
3. utils/kb.py
4. config.yaml
5. filters\CardFilter.py
6. filters\ProfileFilter.py

## Дополнительные условия использования

Если вы хотите изменить или перераспространить код, вы должны:
1. Создать форк репозитория (fork).
2. Вносить изменения в ваш форк и ссылаться на оригинальный репозиторий.

Любые изменения в коде должны быть доступны через ваш публичный форк. При изменении исходного кода отсылаться на оригинальный [репозиторий](https://github.com/Faustyu1/CardsBot).
СЛАВА БОГУ КЛАУДИАУДИСЛАВА БОГУ КЛАУДИАУДИСЛАВА БОГУ КЛАУДИАУДИ


