from typing import List
from dataclasses import dataclass
from environs import Env

@dataclass
class Telegram:
    token: str

@dataclass
class Flyer:
    token: str

@dataclass
class CryptoPay:
    token: str

@dataclass
class Database:
    driver: str
    host: str
    port: int
    database: str
    user: str
    password: str

@dataclass
class Bot:
    telegram: Telegram
    cryptoPay: CryptoPay
    flyer: Flyer
    admins: List[int]

@dataclass
class App:
    bot: Bot
    database: Database

def load_config(path: str | None = None) -> App:
    env = Env()
    env.read_env(path)

    return App(
        bot=Bot(
            telegram=Telegram(
                token=env.str("BOT_TOKEN"),
            ),
            cryptoPay=CryptoPay(
                token=env.str("CRYPTO_TOKEN"),
            ),
            flyer=Flyer(
                token=env.str("FLYER_TOKEN"),
            ),
            admins=list(map(int, env.list("ADMIN_IDS"))),
        ),
        database=Database(
            driver=env.str("DB_DRIVER"),
            host=env.str("DB_HOST"),
            port=env.int("DB_PORT"),
            database=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASSWORD"),
        ),
    )

app = load_config()
settings = app.bot
database = app.database