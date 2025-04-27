from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager
from backend.settings.database import DatabaseSettings

__all__ = ["get_connection_string", "get_db_session", "get_engine"]


def get_connection_string(manage: bool = False):
    settings = DatabaseSettings()

    return "postgresql+asyncpg://%s:%s@%s:%i/%s" % (
        settings.DATABASE_USER,
        settings.DATABASE_PASSWORD,
        settings.DATABASE_HOST,
        settings.DATABASE_PORT,
        settings.DATABASE_NAME if not manage else "postgres",
    )

def get_engine(manage: bool = False):
    return create_async_engine(get_connection_string(manage), echo=False, future=True,)


@asynccontextmanager
async def get_db_session():
    session = None
    try:
        engine = get_engine()
        async_session = async_sessionmaker(autocommit=False, bind=engine)
        session = async_session()

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

    engine = get_engine(manage=True)
    async with engine.connect() as conn:
       await conn.execute(text(f"COMMIT;"))
       await conn.execute(text(f"DROP DATABASE {settings.DATABASE_NAME} WITH (FORCE);"))


async def create_database():
    from backend.database.functions import get_engine
    from sqlalchemy import text

    settings = DatabaseSettings()
    
    engine = get_engine(manage=True)
    async with engine.connect() as conn:
       await conn.execute(text(f"COMMIT;"))
       await conn.execute(text(f"CREATE DATABASE {settings.DATABASE_NAME};"))
