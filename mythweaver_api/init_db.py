#!/usr/bin/env python3
"""
Database initialization and seeding script
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, AsyncSessionLocal
from app.models import Base
from app.services.scenario_service import ScenarioService


async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")


async def seed_scenarios():
    """Seed database with demo scenarios"""
    async with AsyncSessionLocal() as db:
        scenario_service = ScenarioService(db)
        await scenario_service.seed_scenarios()
    print("✅ Scenarios seeded")


async def main():
    """Main initialization function"""
    print("🚀 Initializing Whisperbound DM Backend...")
    
    try:
        await create_tables()
        await seed_scenarios()
        print("✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return 1
    
    finally:
        await engine.dispose()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)