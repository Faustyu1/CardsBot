from database.group import get_all_groups_with_bot_ids
from database.models import Base
from utils.loader import engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
