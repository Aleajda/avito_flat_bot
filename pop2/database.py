# database.py
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
import config

# Создаем движок БД
engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Flat(Base):
    __tablename__ = "flats"

    id: Mapped[int] = mapped_column(primary_key=True)
    avito_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(BigInteger)
    district: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)