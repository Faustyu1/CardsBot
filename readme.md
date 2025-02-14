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
3. Создайте и заполните файл config.yaml
```yaml
bot:
  telegram:
    token: "token"
  cryptoPay:
    token: "token"
  flyer:
    token: "token"
  admins: [77000]
database:
  driver: "postgresql+asyncpg"
  host: "localhost"
  port: 5432
  database: "komaru_cards"
  user: "postgres"
  password: "postgres"
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
