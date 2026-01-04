from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, Integer, DateTime, Float
from datetime import datetime
import config

# Если в config.py еще не поменял, раскомментируй строку ниже для SQLite:
# config.DATABASE_URL = "sqlite+aiosqlite:///./avito_ads.db"

engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    avito_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)

    # Новое поле: цена за квадратный метр
    price_per_meter: Mapped[float] = mapped_column(Float, nullable=True)

    url: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String, nullable=True)
    published_at: Mapped[str] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)


async def init_db():
    async with engine.begin() as conn:
        # Для SQLite это создаст файл avito_ads.db в папке с проектом
        await conn.run_sync(Base.metadata.create_all)