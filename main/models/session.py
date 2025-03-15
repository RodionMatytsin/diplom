from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class SessionHandler:
    __instance = None

    def __init__(self, engine):
        SessionHandler.__instance = self
        self.session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session() as session:
            try:
                yield session
            except Exception as e:
                print(f'Error Session: {e}')
            finally:
                await session.commit()
                await session.close()

    @staticmethod
    def create(engine):
        SessionHandler.__instance = SessionHandler(engine)
        return SessionHandler.__instance.get_async_session
