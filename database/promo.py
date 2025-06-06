import datetime
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.loader import engine
from .models import Promo, User
from .premium import add_premium, check_premium
from .user import check_last_get, IsAlreadyResetException


async def create_promo(
    code: str,
    link: str,
    action: str,
    days_add: Optional[int],
    channel_id: int,
    activation_limit: int,
    expiration_time: datetime,
) -> Promo:
    async with AsyncSession(engine) as session:
        promo = Promo(
            code=code,
            link=link,
            action=action,
            activation_limit=activation_limit,
            expiration_time=expiration_time,
            days_add=days_add,
            channel_id=channel_id,
        )
        session.add(promo)
        await session.commit()
        promo = (
            await session.execute(select(Promo).where(Promo.code == code))
        ).scalar_one()
        return promo


async def delete_promo(code: str) -> None:
    async with AsyncSession(engine) as session:
        promo = (
            await session.execute(select(Promo).where(Promo.code == code))
        ).scalar_one()
        await session.delete(promo)
        await session.commit()


async def get_promo(code: str) -> Promo:
    async with AsyncSession(engine) as session:
        promo = (
            await session.execute(select(Promo).where(Promo.code == code))
        ).scalar_one_or_none()
        return promo


async def add_activation(code: str) -> None:
    async with AsyncSession(engine) as session:
        promo = (
            await session.execute(select(Promo).where(Promo.code == code))
        ).scalar_one()
        promo.activation_counts += 1
        await session.commit()


async def promo_use(telegram_id: int, promo: Promo) -> None:
    async with AsyncSession(engine) as session:
        user: Optional[User] = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()

        if not user:
            raise ValueError("Пользователь не найден")

        user.expired_promo_codes = (user.expired_promo_codes or []) + [promo.code]

        if promo.action == "reset_cd":
            if await check_last_get(
                user.last_usage, await check_premium(user.premium_expire)
            ):
                raise IsAlreadyResetException
            user.last_usage = datetime.now() - timedelta(hours=3)
        elif promo.action == "add_premium":
            await add_premium(user.telegram_id, timedelta(days=promo.days_add))
        else:
            raise ValueError("Неизвестное действие")

        await add_activation(promo.code)
        await session.commit()
