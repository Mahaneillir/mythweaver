"""
Test script to check if mythweaver_characters table exists
"""
import asyncio
from app.core.database import engine
from sqlalchemy import text


async def check_table():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'mythweaver_characters';
            """)
        )
        exists = result.fetchone() is not None
        print(f"mythweaver_characters table exists: {exists}")
        
        if not exists:
            print("Need to run migration")
        else:
            print("✅ Table already exists")


if __name__ == "__main__":
    asyncio.run(check_table())
