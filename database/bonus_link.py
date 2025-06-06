import random
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import BonusLink
from utils.loader import engine


def generate_random_string(length=14):
    random_string = ""
    random_str_seq = string.ascii_letters + string.digits
    for i in range(0, length):
        if i % length == 0 and i != 0:
            random_string += "-"
        random_string += str(random_str_seq[random.randint(0, len(random_str_seq) - 1)])
    return random_string


async def create_bonus_link(
    for_user_id: int,
) -> BonusLink:
    ref_link: str = generate_random_string()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        ref_link_model = BonusLink(code=ref_link, for_user_id=for_user_id)
        session.add(ref_link_model)
        await session.commit()
        return ref_link_model


async def delete_bonus_link(bonus_link: str) -> None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        bonus_link_model = (
            await session.execute(select(BonusLink).where(BonusLink.code == bonus_link))
        ).scalar_one_or_none()
        if bonus_link_model is None:
            return
        await session.delete(bonus_link_model)
        await session.commit()


async def get_bonus_link(code: str) -> BonusLink | None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        return (
            await session.execute(select(BonusLink).where(BonusLink.code == code))
        ).scalar_one_or_none()


async def deactivate_bonus_link(code: str):
    async with AsyncSession(engine, expire_on_commit=False) as session:
        bonus_model = (
            await session.execute(select(BonusLink).where(BonusLink.code == code))
        ).scalar_one_or_none()

        if bonus_model is None:
            raise KeyError(f"Didn't found bonus link with code {code}")
        
        if bonus_model is not None:
            bonus_model.is_active = False  # type: ignore
            await session.commit()
