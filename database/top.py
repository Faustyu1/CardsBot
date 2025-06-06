from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from database.models import User
from database.premium import check_premium
from utils.loader import engine


async def get_top_users_by_cards():
    async with AsyncSession(engine) as session:
        top_users = (
            (
                await session.execute(
                    select(User)
                    .order_by(desc(func.cardinality(User.cards)))
                    .filter(func.cardinality(User.cards) > 0)
                    .limit(10)
                )
            )
            .scalars()
            .all()
        )
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [
                [i, icon, top_user.nickname, len(top_user.cards), top_user.telegram_id]
            ]
            i += 1
        return top


async def get_top_users_by_points():
    async with AsyncSession(engine) as session:
        top_users = (
            (await session.execute(select(User).order_by(desc(User.points)).limit(10)))
            .scalars()
            .all()
        )
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.nickname, top_user.points]]
            i += 1
        return top


async def get_top_users_by_all_points():
    async with AsyncSession(engine) as session:
        top_users = (
            (
                await session.execute(
                    select(User).order_by(desc(User.all_points)).limit(10)
                )
            )
            .scalars()
            .all()
        )
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.nickname, top_user.all_points]]
            i += 1
        return top


async def get_me_on_top(by, telegram_id: int):
    async with AsyncSession(engine) as session:
        position = (
            await session.execute(
                select(1 + count("*")).where(
                    by
                    > select(by)
                    .where(User.telegram_id == telegram_id)
                    .scalar_subquery()
                )
            )
        ).scalar_one()
        return position
