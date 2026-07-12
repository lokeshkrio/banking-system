# test_db.py

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://lokeshkr:password123@localhost:5432/unitybankx"
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)


async def main():
    async with engine.begin():
        print("✅ Connected successfully!")


asyncio.run(main())
