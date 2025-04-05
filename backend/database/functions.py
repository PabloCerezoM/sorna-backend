from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from backend.settings.database import DatabaseSettings

__all__ = ["get_connection_string", "get_db_session", "get_engine"]


def get_connection_string():
    settings = DatabaseSettings()

    return "postgresql+asyncpg://%s:%s@%s:%i/%s" % (
        settings.DATABASE_USER,
        settings.DATABASE_PASSWORD,
        settings.DATABASE_HOST,
        settings.DATABASE_PORT,
        settings.DATABASE_NAME,
    )

def get_engine():
    return create_async_engine(get_connection_string(), echo=False, future=True,)


@asynccontextmanager
async def get_db_session():
    session = None
    try:
        engine = get_engine()
        async_session = async_sessionmaker(autocommit=False, bind=engine)

        async with async_session() as session:
            yield session
    
    except:
        if session is not None:
            await session.rollback()
        raise

    finally:
        if session is not None:
            await session.close()


async def drop_database():
    from backend.database.functions import get_engine
    from sqlalchemy import text
    
    settings = DatabaseSettings()

    engine = get_engine()
    async with engine.connect() as conn:
       await conn.execute(text(f"COMMIT;"))
       await conn.execute(text(f"DROP DATABASE {settings.DATABASE_NAME};"))


async def create_database():
    from backend.database.functions import get_engine
    from sqlalchemy import text

    settings = DatabaseSettings()
    
    engine = get_engine()
    async with engine.connect() as conn:
       await conn.execute(text(f"COMMIT;"))
       await conn.execute(text(f"CREATE DATABASE {settings.DATABASE_NAME};"))
