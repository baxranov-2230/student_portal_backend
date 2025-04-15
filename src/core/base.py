from sqlalchemy.ext.asyncio import AsyncSession , create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.core.config import settings


engine = create_async_engine(settings.connection_string , echo = True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit = False,
)

async def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()

Base = declarative_base()