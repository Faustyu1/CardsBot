# CardsBot for funny in Telegram

## Запуск бота

1. Создайте и активируйте venv
```bash
python3 -m venv venv
source venv/bin/activate
 ```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Создайте и заполните файл .env
```.env
BOT_TOKEN=1234343:AABBCCEE
ADMIN_IDS=77000,77001
CRYPTO_TOKEN=1234343:AABBOOCCEE
FLYER_TOKEN=FL-lekLE-lekLE-lekLE-lekLE

# Database Configuration
DB_DRIVER=postgresql+asyncpg
DB_HOST=host
DB_PORT=5432
DB_NAME=folt_copy
DB_USER=user
DB_PASSWORD="password"
```
4. Запустите бота
```bash
python3 main.py
```

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

Любые изменения в коде должны быть доступны через ваш публичный форк.
СЛАВА БОГУ КЛАУДИАУДИСЛАВА БОГУ КЛАУДИАУДИСЛАВА БОГУ КЛАУДИАУДИ


