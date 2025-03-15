from sqlalchemy import Column, ForeignKey, BigInteger, SmallInteger, Float, String, DateTime, \
    Text, Boolean, func, text, UUID, Integer, ARRAY, PrimaryKeyConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
import main.config as config


class Base(AsyncAttrs, DeclarativeBase):
    pass


# Таблица пользователей
class Users(Base):
    __tablename__ = 'users'
    guid = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True,
        server_default=text('uuid7()'),
        primary_key=True,
        autoincrement=False
    )


# alembic init -t async main/alembic
# alembic revision --autogenerate -m "init alembic"
# alembic upgrade head


engine = create_async_engine(
    f'postgresql+asyncpg://{config.DATABASE_USER}'
    f':{config.DATABASE_PASSWORD}'
    f'@{config.DATABASE_IP}:{config.DATABASE_PORT}'
    f'/{config.DATABASE_NAME}',
    echo=False,
    pool_recycle=300,
    query_cache_size=0,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=2,
    pool_use_lifo=True
)
