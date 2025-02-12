from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Group
from utils.loader import engine


async def create_group(group_id: int, title: str) -> Group:
    async with AsyncSession(engine) as session:
        group = Group(group_id=group_id, title=title, comments_on=True)
        session.add(group)
        await session.commit()
        group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one()
        return group
    

async def set_comments_active(chat_id: int, to_set: bool) -> None:
    async with AsyncSession(engine) as session:
        group: Group = (await session.execute(select(Group).where(Group.group_id == chat_id))).scalar_one_or_none()
        
        if group:
            group.comments_on = to_set
            await session.commit()
            
            updated_group = (await session.execute(
                select(Group).where(Group.group_id == chat_id)
            )).scalar_one_or_none()


async def get_group(group_id: int) -> Group:
    async with AsyncSession(engine) as session:
        group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one_or_none()
        return group


async def get_group_with_bot_count():
    async with (AsyncSession(engine) as session):
        group_count = (await session.execute(
            select(func.count(Group.id))
            .where(Group.in_group == True))
                       ).scalar_one_or_none()
        return group_count


async def get_all_groups_ids(offset: int = 0, limit: int = None) -> [Group]:
    async with AsyncSession(engine) as session:
        groups = (await session.execute(select(Group.group_id).limit(limit).offset(offset))).scalars().all()
        return groups


async def get_all_groups_with_bot_ids() -> [Group]:
    async with AsyncSession(engine) as session:
        groups = (await session.execute(select(Group.group_id).where(Group.in_group == True))).scalars().all()
        return groups


async def in_group_change(group_id: int, status: bool) -> None:
    async with AsyncSession(engine) as session:
        group: Group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one_or_none()
        group.in_group = status
        await session.commit()


async def get_group_count():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(func.count(Group.id)))
        return result.scalar_one()


async def update_last_activity_group(telegram_id: int):
    async with AsyncSession(engine) as session:
        group: Group = (await session.execute(select(Group).where(Group.group_id == telegram_id))).scalar_one_or_none()
        group.last_activity = datetime.now().date()
        await session.commit()


async def set_group_refer_code(group_id: int, code: str):
    async with AsyncSession(engine) as session:
        group: Group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one_or_none()
        group.from_link = code
        await session.commit()
