import datetime
from typing import Union, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import App, Group, User
from utils.loader import engine


async def get_users_count_created_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(func.count(User.id))
            .where(and_(User.created_at == data, User.in_pm == True))
        )).scalar_one()


async def get_users_count_last_active_today() -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(func.count(User.id))
            .where(User.last_activity == datetime.datetime.now().date())
        )).scalar_one()


async def get_groups_count_created_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(func.count(Group.id))
            .where(Group.added_at == data)
        )).scalar_one()


async def get_groups_count_last_active_today() -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(func.count(Group.id))
            .where(Group.last_activity == datetime.datetime.now().date())
        )).scalar_one()


async def update_yesterday_last_activities() -> None:
    async with AsyncSession(engine) as session:
        app: Optional[App] = (await session.execute(
            select(App).where(App.id == 1)
        )).scalar_one_or_none()

        if app:
            app.yesterday_groups_active = await get_groups_count_last_active_today()
            app.yesterday_users_active = await get_users_count_last_active_today()
            await session.commit()


async def get_yesterday_groups_active() -> Union[int, str]:
    async with AsyncSession(engine) as session:
        count: Optional[int] = (await session.execute(
            select(App.yesterday_groups_active).where(App.id == 1)
        )).scalar_one_or_none()
        return count if count is not None else "Вернитесь после 23.59"


async def get_yesterday_users_active() -> Union[int, str]:
    async with AsyncSession(engine) as session:
        count: Optional[int] = (await session.execute(
            select(App.yesterday_users_active).where(App.id == 1)
        )).scalar_one_or_none()
        return count if count is not None else "Активность не готова, вернитесь после 23.59"


async def create_app_if_not_exist() -> None:
    async with AsyncSession(engine) as session:
        app: Optional[App] = (await session.execute(
            select(App).where(App.id == 1)
        )).scalar_one_or_none()
        if app is None:
            app = App(id=1, yesterday_users_active=None, yesterday_groups_active=None)
            session.add(app)
            await session.commit()


async def get_users_with_link_count(link: str) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(func.count(User.id)).where(User.from_link == link)
        )).scalar_one()


async def get_groups_with_link_count(link: str) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(func.count(Group.id)).where(Group.from_link == link)
        )).scalar_one()


async def get_all_groups_with_link(link: str) -> List[int]:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(Group.group_id).where(Group.from_link == link)
        )).scalars().all()


async def get_all_users_with_link(link: str) -> List[int]:
    async with AsyncSession(engine) as session:
        return (await session.execute(
            select(User.telegram_id).where(User.from_link == link)
        )).scalars().all()
