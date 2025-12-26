"""
Integration tests for campaign creation workflow.

Tests the complete flow:
1. User signup
2. User login
3. Create campaign with character
4. Retrieve campaign
5. Verify character stats
"""
import pytest
import random
import string
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


def random_username(prefix="testuser"):
    """Generate a random username for testing"""
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{suffix}"


@pytest.mark.asyncio
async def test_full_campaign_creation_flow(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test the complete campaign creation flow from signup to campaign retrieval.
    """
    # Step 1: Signup
    username = random_username("campaign")
    email = f"{username}@example.com"
    password = "TestPassword123!"

    signup_data = {
        "email": email,
        "password": password,
        "username": username,
    }
    signup_response = await async_client.post("/auth/register", json=signup_data)
    assert signup_response.status_code in [200, 201], f"Signup failed: {signup_response.text}"

    # Step 2: Login
    login_response = await async_client.post(
        "/auth/token",
        data={
            "username": email,
            "password": password,
        }
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token_data = login_response.json()
    access_token = token_data["access_token"]
    
    # Step 3: Create campaign with character
    campaign_request = {
        "campaign_name": "Test Campaign",
        "template_id": "broken_kingdom",
        "character": {
            "name": "Aria Shadowblade",
            "origin_id": "street_urchin",
            "path_id": "shadow",
            "attributes": {
                "might": 3,
                "agility": 6,
                "wits": 4,
                "presence": 2
            },
            "skills": {
                "blade": 0,
                "bow": 0,
                "brawl": 0,
                "sneak": 2,
                "survival": 1,
                "lore": 0,
                "craft": 0,
                "influence": 0,
                "insight": 1,
                "channel": 0
            },
            "talent_ids": ["smoke_step", "backstab"]
        },
        "settings": {
            "tone": "gritty",
            "content_limits": ["none"],
            "difficulty": "balanced"
        }
    }
    
    create_response = await async_client.post(
        "/campaign/create",
        json=campaign_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert create_response.status_code == 201, f"Failed: {create_response.text}"
    campaign_data = create_response.json()
    
    # Verify response structure
    assert "campaign_id" in campaign_data
    assert "character_id" in campaign_data
    assert "opening_narration" in campaign_data
    assert "suggested_actions" in campaign_data
    
    # Verify opening narration contains origin-specific context
    assert len(campaign_data["opening_narration"]) > 100
    assert "street" in campaign_data["opening_narration"].lower() or "urchin" in campaign_data["opening_narration"].lower()
    
    # Verify suggested actions
    assert len(campaign_data["suggested_actions"]) > 0
    
    campaign_id = campaign_data["campaign_id"]
    character_id = campaign_data["character_id"]
    
    # Step 4: Retrieve campaign
    get_response = await async_client.get(
        f"/campaign/{campaign_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert get_response.status_code == 200
    retrieved_campaign = get_response.json()
    
    # Verify campaign data
    assert retrieved_campaign["id"] == campaign_id
    assert retrieved_campaign["name"] == "Test Campaign"
    assert retrieved_campaign["template_id"] == "broken_kingdom"
    assert retrieved_campaign["current_location"] == "The Crossroads Inn"
    assert retrieved_campaign["chapter_number"] == 1
    
    # Step 5: Verify character stats
    assert retrieved_campaign["character"] is not None
    character = retrieved_campaign["character"]
    
    assert character["id"] == character_id
    assert character["name"] == "Aria Shadowblade"
    assert character["origin_id"] == "street_urchin"
    assert character["path_id"] == "shadow"
    
    # Verify attributes
    assert character["might_score"] == 3
    assert character["agility_score"] == 6
    assert character["wits_score"] == 4
    assert character["presence_score"] == 2
    
    # Verify derived stats
    # HP = 8 + (might * 2) = 8 + (3 * 2) = 14
    assert character["max_hp"] == 14
    assert character["current_hp"] == 14
    
    # Focus = 4 + wits + presence = 4 + 4 + 2 = 10
    assert character["max_focus"] == 10
    assert character["current_focus"] == 10
    
    # Supplies = 3 (default)
    assert character["supplies"] == 3
    
    # Inventory slots = might // 2 = 3 // 2 = 1
    assert character["inventory_slots"] == 1
    
    # Verify skills
    assert character["skills"]["sneak"] == 2
    assert character["skills"]["survival"] == 1
    assert character["skills"]["insight"] == 1


@pytest.mark.asyncio
async def test_campaign_creation_with_blade_character(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test campaign creation with a Blade archetype character.
    """
    # Signup and login
    username = random_username("blade")
    email = f"{username}@example.com"
    password = "TestPassword123!"

    signup_data = {
        "email": email,
        "password": password,
        "username": username,
    }
    await async_client.post("/auth/register", json=signup_data)

    login_response = await async_client.post(
        "/auth/token",
        data={
            "username": email,
            "password": password,
        }
    )
    access_token = login_response.json()["access_token"]
    
    # Create campaign with Blade character
    campaign_request = {
        "campaign_name": "Blade's Journey",
        "template_id": "broken_kingdom",
        "character": {
            "name": "Kael Ironfist",
            "origin_id": "veteran",
            "path_id": "blade",
            "attributes": {
                "might": 6,
                "agility": 4,
                "wits": 3,
                "presence": 2
            },
            "skills": {
                "blade": 2,
                "bow": 0,
                "brawl": 1,
                "sneak": 0,
                "survival": 1,
                "lore": 0,
                "craft": 0,
                "influence": 0,
                "insight": 0,
                "channel": 0
            },
            "talent_ids": ["riposte", "shield_ally"]
        }
    }
    
    create_response = await async_client.post(
        "/campaign/create",
        json=campaign_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert create_response.status_code == 201
    campaign_data = create_response.json()

    # Verify veteran-specific narration (check for military/veteran-related keywords)
    narration_lower = campaign_data["opening_narration"].lower()
    veteran_keywords = ["veteran", "soldier", "war", "battle", "unit", "discharge", "military", "combat"]
    assert any(keyword in narration_lower for keyword in veteran_keywords), \
        f"Expected veteran-themed narration, got: {campaign_data['opening_narration']}"
    
    # Get campaign and verify stats
    campaign_id = campaign_data["campaign_id"]
    get_response = await async_client.get(
        f"/campaign/{campaign_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    character = get_response.json()["character"]
    
    # HP = 8 + (6 * 2) = 20
    assert character["max_hp"] == 20
    
    # Focus = 4 + 3 + 2 = 9
    assert character["max_focus"] == 9
    
    # Inventory slots = 6 // 2 = 3
    assert character["inventory_slots"] == 3


@pytest.mark.asyncio
async def test_campaign_creation_validation_errors(async_client: AsyncClient):
    """
    Test that campaign creation fails with invalid character data.
    """
    # Signup and login
    username = random_username("validation")
    email = f"{username}@example.com"
    password = "TestPassword123!"

    signup_data = {
        "email": email,
        "password": password,
        "username": username,
    }
    await async_client.post("/auth/register", json=signup_data)

    login_response = await async_client.post(
        "/auth/token",
        data={
            "username": email,
            "password": password,
        }
    )
    access_token = login_response.json()["access_token"]
    
    # Test 1: Invalid attributes sum (should be 15)
    invalid_request = {
        "campaign_name": "Invalid Campaign",
        "template_id": "broken_kingdom",
        "character": {
            "name": "Invalid Character",
            "origin_id": "street_urchin",
            "path_id": "shadow",
            "attributes": {
                "might": 10,  # Sum is 22, not 15
                "agility": 6,
                "wits": 4,
                "presence": 2
            },
            "skills": {
                "blade": 0, "bow": 0, "brawl": 0, "sneak": 2,
                "survival": 1, "lore": 0, "craft": 0, "influence": 0,
                "insight": 1, "channel": 0
            },
            "talent_ids": ["smoke_step", "backstab"]
        }
    }
    
    response = await async_client.post(
        "/campaign/create",
        json=invalid_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Pydantic validation returns 422 (Unprocessable Entity), not 400
    assert response.status_code == 422
    assert "attribute" in response.text.lower()
    
    # Test 2: Wrong number of skills (should be exactly 3)
    invalid_request["character"]["attributes"] = {
        "might": 3, "agility": 6, "wits": 4, "presence": 2
    }
    invalid_request["character"]["skills"]["sneak"] = 0  # Now only 2 skills selected
    
    response = await async_client.post(
        "/campaign/create",
        json=invalid_request,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Pydantic validation returns 422 (Unprocessable Entity)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_campaign_not_found(async_client: AsyncClient):
    """
    Test that retrieving a non-existent campaign returns 404.
    """
    # Signup and login
    username = random_username("notfound")
    email = f"{username}@example.com"
    password = "TestPassword123!"

    signup_data = {
        "email": email,
        "password": password,
        "username": username,
    }
    await async_client.post("/auth/register", json=signup_data)

    login_response = await async_client.post(
        "/auth/token",
        data={
            "username": email,
            "password": password,
        }
    )
    access_token = login_response.json()["access_token"]
    
    # Try to get a non-existent campaign
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await async_client.get(
        f"/campaign/{fake_uuid}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 404
