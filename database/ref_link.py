from typing import Dict, List

from aiogram.utils.deep_linking import create_deep_link
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RefLink
from utils.loader import engine


async def get_ref_link(code: str) -> RefLink:
    async with AsyncSession(engine) as session:
        ref_link = (
            await session.execute(select(RefLink).where(RefLink.code == code))
        ).scalar_one_or_none()
        return ref_link


async def create_ref_link(code: str) -> RefLink:
    async with AsyncSession(engine) as session:
        ref_link = RefLink(code=code)
        session.add(ref_link)
        await session.commit()
        return ref_link


async def delete_ref_link(code: str) -> None:
    async with AsyncSession(engine) as session:
        ref_link = (
            await session.execute(select(RefLink).where(RefLink.code == code))
        ).scalar_one_or_none()
        if ref_link is None:
            return
        await session.delete(ref_link)
        await session.commit()


async def get_links(code: str, bot_username) -> Dict[str, str]:
    link_user = create_deep_link(bot_username, "start", f"ref_{code}")
    link_group = create_deep_link(bot_username, "startgroup", f"ref_{code}")
    return {"link_user": link_user, "link_group": link_group}


async def get_all_links() -> List[str]:
    async with AsyncSession(engine) as session:
        ref_links = await session.execute(select(RefLink.code))
        return ref_links.scalars().all()
