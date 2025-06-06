from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy import func, select, update, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB

from database.models import User
from utils.loader import engine


async def create_user(telegram_id: int, username: str, in_pm: bool = False) -> User:
    async with AsyncSession(engine) as session:
        if username:
            user = User(telegram_id=telegram_id, nickname=username, in_pm=in_pm)
        else:
            user = User(telegram_id=telegram_id, in_pm=in_pm)
        session.add(user)
        await session.commit()
        user = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one()
        return user


async def get_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        return user


async def get_user_with_pm_count():
    async with AsyncSession(engine) as session:
        user_count = (
            await session.execute(select(func.count(User.id)).where(User.in_pm == True))
        ).scalar_one_or_none()
        return user_count


async def set_love_card(telegram_id: int, love_card_id: int, is_limited: bool):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        if user is None:
            return False

        user.love_card = {"id": love_card_id, "is_limited": is_limited}
        await session.commit()
        return True


async def update_last_get(telegram_id: int):
    await set_last_get(telegram_id, datetime.now())


async def set_last_get(telegram_id: int, time: datetime):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.last_usage = time
        await session.commit()


async def add_points(telegram_id: int, points: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.points += points
        user.all_points += points
        await session.commit()


async def add_card(telegram_id: int, card_id: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.cards += [card_id]
        user.card_count += 1
        await session.commit()


async def change_username(telegram_id: int, username: str):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.nickname = username
        await session.commit()


async def is_nickname_taken(nickname: str) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.nickname == nickname))
        users = result.scalars().all()
        return len(users) > 0


async def clear_season():
    async with AsyncSession(engine) as session:
        users: [User] = (await session.execute(select(User))).scalars().all()
        for user in users:
            user.cards = []
            user.points = 0
            user.last_usage = None
        await session.commit()
        return


async def ban_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.is_banned = True
        await session.commit()
        return


async def upgrade_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.status = "ADMIN"
        await session.commit()
        return


async def unban_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.is_banned = False
        await session.commit()
        return


async def get_all_users_ids(offset: int = 0, limit: int = None) -> [User]:
    async with AsyncSession(engine) as session:
        users: Dict[User] = (
            (
                await session.execute(
                    select(User.telegram_id).limit(limit).offset(offset)
                )
            )
            .scalars()
            .all()
        )
        return users


async def get_all_users_with_pm_ids() -> [User]:
    async with AsyncSession(engine) as session:
        users: Dict[User] = (
            (await session.execute(select(User.telegram_id).where(User.in_pm == True)))
            .scalars()
            .all()
        )
        return users


class IsAlreadyResetException(Exception):
    pass


async def check_last_get(last_get: datetime, is_premium: bool):
    if last_get is None:
        return True
    time_difference = datetime.now() - last_get
    if is_premium:
        if time_difference >= timedelta(hours=3):
            return True
        else:
            return False
    else:
        if time_difference >= timedelta(hours=4):
            return True
        else:
            return False


async def in_pm_change(telegram_id: int, status: bool) -> None:
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.in_pm = status
        await session.commit()


async def get_user_count():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(func.count(User.telegram_id)))
        return result.scalar_one()


async def update_last_activity(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.last_activity = datetime.now().date()
        await session.commit()


async def update_last_bonus_get(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.last_bonus_get = datetime.now()
        await session.commit()


async def set_user_refer_code(telegram_id: int, code: str):
    async with AsyncSession(engine) as session:
        user: User = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()
        user.from_link = code
        await session.commit()


async def add_coins(
    telegram_id: int, coins: int, username: str = None, in_pm: bool = False
) -> bool:
    user = await get_user(telegram_id)
    if user is None:
        user = await create_user(telegram_id, username or "Гость", in_pm)

    async with AsyncSession(engine) as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one()
        user.coins += coins
        await session.commit()
        return True


async def get_coins(telegram_id: int) -> int:
    user = await get_user(telegram_id)
    if user is None:
        return 0

    async with AsyncSession(engine) as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == telegram_id))
        ).scalar_one_or_none()

        return user.coins if user else 0


async def set_luck(telegram_id: int, luck: bool):
    async with AsyncSession(engine) as session:
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(luck=luck)
        )
        await session.commit()


async def get_luck(telegram_id: int) -> bool:
    async with AsyncSession(engine) as session:
        user = (
            await session.execute(
                select(User.luck).where(User.telegram_id == telegram_id)
            )
        ).scalar_one_or_none()

        return user if user is not None else False


async def add_dice_get(telegram_id: int):
    async with AsyncSession(engine) as session:
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(last_dice_play=datetime.now())
        )
        await session.commit()


async def add_limited_card_to_user(user_id: int, card_id: int):
    async with AsyncSession(engine) as session:
        await session.execute(
            update(User)
            .where(User.telegram_id == user_id)
            .values(
                limited_cards=func.coalesce(User.limited_cards, cast([], JSONB)).concat(
                    cast([card_id], JSONB)
                )
            )
        )
        await session.commit()


async def check_user_has_limited_card(user_id: int, card_id: int) -> bool:
    async with AsyncSession(engine) as session:
        user = (
            await session.execute(select(User).where(User.telegram_id == user_id))
        ).scalar_one_or_none()
        if not user or not user.limited_cards:
            return False
        return card_id in user.limited_cards
