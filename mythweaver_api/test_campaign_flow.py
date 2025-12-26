"""
Manual test script for campaign creation flow.
Run this with the server running to test the complete flow.
"""
import httpx
import asyncio
import json


BASE_URL = "http://localhost:8000"


async def test_campaign_creation():
    """Test campaign creation end-to-end"""
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("Campaign Creation Flow Test")
        print("=" * 60)
        
        # Use a unique email for each test run
        import time
        unique_id = int(time.time())
        
        # Step 1: Register
        print("\n1. Registering new user...")
        register_data = {
            "email": f"testuser{unique_id}@example.com",
            "password": "TestPassword123!",
            "username": f"testuser{unique_id}",
        }
        
        register_response = await client.post(
            f"{BASE_URL}/auth/register",
            json=register_data
        )
        
        if register_response.status_code in [200, 201]:
            print("✅ Registration successful")
            token_data = register_response.json()
            access_token = token_data.get("accessToken") or token_data.get("access_token")
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(register_response.text)
            return
        
        # Step 2: Create Campaign
        print("\n2. Creating campaign with character...")
        campaign_request = {
            "campaign_name": f"Test Campaign {unique_id}",
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
        
        create_response = await client.post(
            f"{BASE_URL}/campaign/create",
            json=campaign_request,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if create_response.status_code == 201:
            print("✅ Campaign created successfully")
            campaign_data = create_response.json()
            
            print(f"\nCampaign ID: {campaign_data['campaign_id']}")
            print(f"Character ID: {campaign_data['character_id']}")
            print(f"\nOpening Narration ({len(campaign_data['opening_narration'])} chars):")
            print("-" * 60)
            print(campaign_data['opening_narration'])
            print("-" * 60)
            print(f"\nSuggested Actions ({len(campaign_data['suggested_actions'])} actions):")
            for i, action in enumerate(campaign_data['suggested_actions'], 1):
                print(f"{i}. {action}")
            
            campaign_id = campaign_data['campaign_id']
            
            # Step 3: Retrieve Campaign
            print("\n3. Retrieving campaign...")
            get_response = await client.get(
                f"{BASE_URL}/campaign/{campaign_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if get_response.status_code == 200:
                print("✅ Campaign retrieved successfully")
                retrieved = get_response.json()
                
                print(f"\nCampaign Details:")
                print(f"  Name: {retrieved['name']}")
                print(f"  Template: {retrieved['template_id']}")
                print(f"  Scene: {retrieved['current_scene_number']}")
                print(f"  Chapter: {retrieved['chapter_number']}")
                print(f"  Tone: {retrieved['tone']}")
                print(f"  Difficulty: {retrieved['difficulty']}")
                
                if retrieved.get('character'):
                    char = retrieved['character']
                    print(f"\nCharacter Details:")
                    print(f"  Name: {char['name']}")
                    print(f"  Origin: {char['origin_id']}")
                    print(f"  Path: {char['path_id']}")
                    print(f"  Attributes: M{char['might_score']} A{char['agility_score']} W{char['wits_score']} P{char['presence_score']}")
                    print(f"  HP: {char['current_hp']}/{char['max_hp']}")
                    print(f"  Focus: {char['current_focus']}/{char['max_focus']}")
                    print(f"  Supplies: {char['supplies']}")
                    
                    # Verify derived stats
                    expected_hp = 8 + (char['might_score'] * 2)  # 8 + (3 * 2) = 14
                    expected_focus = 4 + char['wits_score'] + char['presence_score']  # 4 + 4 + 2 = 10
                    expected_slots = 8 + char['might_score']  # 8 + 3 = 11
                    
                    print(f"\n✅ HP correct: {char['max_hp']} == {expected_hp}")
                    print(f"✅ Focus correct: {char['max_focus']} == {expected_focus}")
                    print(f"✅ Inventory slots calculation: might {char['might_score']} // 2 = {expected_slots}")
                    
                    if char['max_hp'] == expected_hp and char['max_focus'] == expected_focus:
                        print("\n✅✅✅ ALL TESTS PASSED! ✅✅✅")
                    else:
                        print("\n❌ Some stat calculations are incorrect")
                else:
                    print("❌ Character not found in response")
                    
            else:
                print(f"❌ Failed to retrieve campaign: {get_response.status_code}")
                print(get_response.text)
                
        else:
            print(f"❌ Campaign creation failed: {create_response.status_code}")
            print(create_response.text)


if __name__ == "__main__":
    print("\n🚀 Starting manual campaign creation test")
    print("Make sure the server is running on http://localhost:8000\n")
    
    try:
        asyncio.run(test_campaign_creation())
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
