import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.loader import engine
from .models import Card, LimitedCards


async def parse_cards(filename) -> None:
    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)
    data = data["cats"]

    async with AsyncSession(engine) as session:
        for card in data:
            card_id = int(card["id"])

            existing_card = await session.get(Card, card_id)
            if existing_card:
                existing_card.name = card["name"]
                existing_card.points = int(card["points"])
                existing_card.rarity = card["rarity"]
                existing_card.photo = card["photo"]
                existing_card.description = card.get("description", None)
                continue

            db_card = Card(
                id=card_id,
                name=card["name"],
                points=int(card["points"]),
                rarity=card["rarity"],
                photo=card["photo"],
                description=card.get("description", None),
            )
            session.add(db_card)
        await session.commit()


async def parse_limited_cards(filename) -> None:
    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)
    data = data["cats"]

    async with AsyncSession(engine) as session:
        for card in data:
            card_id = int(card["id"])

            existing_card = await session.get(LimitedCards, card_id)
            if existing_card:
                existing_card.name = card["name"]
                existing_card.price = int(card["price"])
                existing_card.edition = int(card["edition"])
                existing_card.photo = card["photo"]
                existing_card.description = card.get("description", None)
                continue

            db_card = LimitedCards(
                id=card_id,
                name=card["name"],
                price=int(card["price"]),
                edition=int(card["edition"]),
                photo=card["photo"],
                description=card.get("description", None),
            )
            session.add(db_card)
        await session.commit()


async def get_card(card_id: int) -> Card | None:
    async with AsyncSession(engine) as session:
        card: Card | None = (
            await session.execute(select(Card).where(Card.id == card_id))
        ).scalar_one_or_none()
        return card


async def get_all_cards() -> list[Card]:
    async with AsyncSession(engine) as session:
        cards = (await session.execute(select(Card))).scalars().all()
        return list(cards)


async def get_lcard(cat_id: int) -> LimitedCards | None:
    async with AsyncSession(engine) as session:
        cat: LimitedCards | None = (
            await session.execute(select(LimitedCards).where(LimitedCards.id == cat_id))
        ).scalar_one_or_none()
        return cat


async def get_all_lcards() -> list[LimitedCards]:
    async with AsyncSession(engine) as session:
        cats = (await session.execute(select(LimitedCards))).scalars().all()
        return list(cats)


async def increment_buy_count(card_id: int):
    """Increment card's buy count by it's ID

    Args:
        card_id (int): Card's id

    Raises:
        KeyError: If card didn't found
    """    
    async with AsyncSession(engine) as session:
        card = (
            await session.execute(
                select(LimitedCards).where(LimitedCards.id == card_id)
            )
        ).scalar_one_or_none()
        if card is None:
            raise KeyError(f"Didn't found card with id {card_id}")
        
        card.buy_count += 1
        await session.commit()
