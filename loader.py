from aiocryptopay import AioCryptoPay, Networks
from aiogram import Bot
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
import config


bot = Bot(token=config.BOT_TOKEN)


url = URL.create(
    drivername="postgresql+asyncpg",
    username="postgres",
    host="127.0.0.1",
    database="komaru_cards",
    password="QwerTY",
)
engine = create_async_engine(url)
async_session: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
crypto = AioCryptoPay(token=config.AIO_TOKEN, network=Networks.TEST_NET)
