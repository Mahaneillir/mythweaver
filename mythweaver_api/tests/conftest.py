"""
Shared test fixtures and configuration for pytest
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
import sys
import os
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import after adding to path
from app.core.database import Base, get_db
from main import app


# Test database URL - use the same database as development (or TEST_DATABASE_URL if set)
# In production, use a separate test database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
if not TEST_DATABASE_URL:
    raise ValueError("DATABASE_URL or TEST_DATABASE_URL environment variable must be set")

# Convert postgresql:// to postgresql+asyncpg:// if needed
if TEST_DATABASE_URL.startswith("postgresql://"):
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session using existing tables"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """Create an async HTTP client for testing"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client"""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Mock AI response"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_character_data():
    """Sample character data for testing"""
    return {
        "id": "char-123",
        "name": "Kira Nightwhisper",
        "character_class": "rogue",
        "race": "halfling",
        "level": 1,
        "experience": 0,
        "stats": {
            "strength": 8,
            "dexterity": 16,
            "constitution": 14,
            "intelligence": 12,
            "wisdom": 13,
            "charisma": 8
        },
        "skills": {
            "proficient": ["stealth", "investigation", "thieves_tools"],
            "improved": []
        },
        "equipment": {
            "weapons": {"primary": "shortsword"},
            "armor": {"body": "leather_armor"},
            "inventory": []
        }
    }


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {
        "id": "sess-456",
        "scenario_id": "mysterious-tavern",
        "character_id": "char-123",
        "current_state": {
            "location": "tavern_main_room",
            "storyProgress": {"discoveredClues": []},
            "npcStates": {"aldric": {"relationship": "neutral"}}
        },
        "action_history": []
    }


@pytest.fixture
def sample_scenario_data():
    """Sample scenario data for testing"""
    return {
        "id": "mysterious-tavern",
        "title": "The Mysterious Tavern",
        "description": "Strange sounds echo from the cellar of the Crooked Crow tavern...",
        "initial_state": {
            "location": "tavern_entrance",
            "openingNarrative": "The heavy wooden door creaks as you enter...",
            "storyProgress": {"discoveredClues": []},
            "npcStates": {"aldric": {"relationship": "neutral", "mood": "welcoming"}}
        }
    }