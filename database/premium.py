from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from utils.loader import engine


async def check_premium(premium_expire: datetime):
    return (
        True
        if premium_expire is not None and premium_expire.date() > datetime.now().date()
        else False
    )


async def get_premium_users() -> [User]:
    async with AsyncSession(engine) as session:
        users: [User] = (
            (
                await session.execute(
                    select(User)
                    .where(User.premium_expire.is_not(None))
                    .where(User.premium_expire > datetime.now())
                )
            )
            .scalars()
            .all()
        )
        return users


async def premium_from_datetime(telegram_id: int, end_date: datetime):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.premium_expire = end_date
        await session.commit()


async def add_premium(telegram_id: int, days: timedelta):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()

        if user.premium_expire is None or datetime.now() >= user.premium_expire:
            user.premium_expire = datetime.now() + days
        else:
            user.premium_expire = user.premium_expire + days

        await session.commit()
