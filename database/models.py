import datetime
from typing import List

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    VARCHAR,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(VARCHAR(64), default="Гость", unique=False)
    cards: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(ARRAY(Integer)), default=[]
    )
    limited_cards = Column(JSONB, nullable=False, default=list)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    all_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_usage: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    love_card: Mapped[dict] = mapped_column(JSONB, nullable=True)
    card_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    premium_expire: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    expired_promo_codes: Mapped[List[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(VARCHAR(80))), default=[], nullable=True
    )
    created_at: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, default=datetime.datetime.now().date()
    )
    last_activity: Mapped[datetime.date] = mapped_column(
        Date, nullable=True, default=datetime.datetime.now().date()
    )
    in_pm: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(
        VARCHAR(40), nullable=False, default="USER", server_default="USER"
    )
    last_bonus_get: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    from_link: Mapped[str] = mapped_column(String, nullable=True, default=None)
    coins: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    luck: Mapped[bool] = mapped_column(Boolean, default=False)
    last_dice_play: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)

    def check_promo_expired(self, promo: str) -> bool:
        return (
            promo in self.expired_promo_codes
            if self.expired_promo_codes is not None
            else False
        )

    def check_bonus_available(self) -> bool:
        if self.last_bonus_get is None:
            return True
        return datetime.datetime.now() >= self.last_bonus_get + datetime.timedelta(
            hours=4
        )


class App(Base):
    __tablename__ = "app"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    yesterday_users_active: Mapped[int] = mapped_column(Integer, nullable=True)
    yesterday_groups_active: Mapped[int] = mapped_column(Integer, nullable=True)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    added_at: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, default=datetime.datetime.now().date()
    )
    last_activity: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, default=datetime.datetime.now().date()
    )
    in_group: Mapped[bool] = mapped_column(Boolean, default=True)
    from_link: Mapped[str] = mapped_column(String, nullable=True, default=None)
    comments_on: Mapped[bool] = mapped_column(Boolean, default=True)


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(80), nullable=False)
    photo: Mapped[str] = mapped_column(VARCHAR(160), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    rarity: Mapped[str] = mapped_column(VARCHAR(80), nullable=False)
    description: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)


class Promo(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(80), nullable=False, unique=True)
    link: Mapped[str] = mapped_column(VARCHAR(160), nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    action: Mapped[str] = mapped_column(VARCHAR(80), nullable=False)
    days_add: Mapped[int] = mapped_column(Integer, nullable=True)
    expiration_time: Mapped[datetime.date] = mapped_column(DateTime, nullable=False)
    activation_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    activation_counts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def is_expiated_counts(self):
        return self.activation_counts >= self.activation_limit

    def is_expiated_time(self):
        return datetime.datetime.now() >= self.expiration_time


class BonusLink(Base):
    __tablename__ = "bonus_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(80), nullable=False, unique=True)
    for_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_active = Column(Boolean, default=True)


class RefLink(Base):
    __tablename__ = "ref_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(80), nullable=False, unique=True)


class LimitedCards(Base):
    __tablename__ = "limited_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    edition: Mapped[int] = mapped_column(BigInteger, nullable=False)
    buy_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String, nullable=True)
    photo: Mapped[str] = mapped_column(String, nullable=False)
