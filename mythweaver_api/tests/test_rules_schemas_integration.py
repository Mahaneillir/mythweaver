"""
Integration test: Rules Engine + Character Schemas
Tests that validation works with Pydantic schemas
"""
import pytest
from app.schemas.character import (
    AttributeScores,
    SkillsDict,
    TalentData,
    BondData,
    CharacterCreate
)
from app.services.rules_engine import (
    calculate_max_hp,
    calculate_max_focus,
    validate_character_creation,
    ValidationError
)


def test_valid_character_creation_with_schemas():
    """Test creating a valid character using Pydantic schemas"""
    
    # Create character data using schemas
    character_data = CharacterCreate(
        name="Kael Ironblade",
        origin_id="veteran",
        path_id="blade",
        attributes=AttributeScores(
            might=6,
            agility=4,
            wits=3,
            presence=2
        ),
        skills=SkillsDict(
            blade=8,
            sneak=4,
            insight=4
        ),
        talent_ids=["riposte", "shield_ally"]
    )
    
    # Verify Pydantic validation passed
    assert character_data.name == "Kael Ironblade"
    assert character_data.attributes.might == 6
    assert character_data.skills.blade == 8
    assert len(character_data.talent_ids) == 2
    
    # Calculate derived stats
    hp = calculate_max_hp(character_data.attributes.might)
    focus = calculate_max_focus(character_data.attributes.wits, character_data.attributes.presence)
    
    assert hp == 20  # 8 + (6 * 2)
    assert focus == 9  # 4 + 3 + 2
    
    print("✅ Character creation with schemas validated successfully")
    print(f"   Name: {character_data.name}")
    print(f"   Origin: {character_data.origin_id}, Path: {character_data.path_id}")
    print(f"   HP: {hp}, Focus: {focus}")


def test_invalid_character_schemas():
    """Test that invalid character data is rejected by Pydantic"""
    
    # Test 1: Invalid attribute sum
    with pytest.raises(ValueError) as exc_info:
        CharacterCreate(
            name="Invalid Character",
            origin_id="veteran",
            path_id="blade",
            attributes=AttributeScores(
                might=8,  # Sum = 17, not 15
                agility=4,
                wits=3,
                presence=2
            ),
            skills=SkillsDict(blade=8, sneak=4, insight=4),
            talent_ids=["riposte", "shield_ally"]
        )
    assert "sum to 15" in str(exc_info.value)
    
    # Test 2: Wrong number of skills
    with pytest.raises(ValueError) as exc_info:
        CharacterCreate(
            name="Invalid Character",
            origin_id="veteran",
            path_id="blade",
            attributes=AttributeScores(might=6, agility=4, wits=3, presence=2),
            skills=SkillsDict(blade=8, sneak=4, insight=4, bow=4),  # 4 skills
            talent_ids=["riposte", "shield_ally"]
        )
    assert "exactly 3 starting skills" in str(exc_info.value)
    
    # Test 3: Wrong number of talents
    with pytest.raises(ValueError) as exc_info:
        CharacterCreate(
            name="Invalid Character",
            origin_id="veteran",
            path_id="blade",
            attributes=AttributeScores(might=6, agility=4, wits=3, presence=2),
            skills=SkillsDict(blade=8, sneak=4, insight=4),
            talent_ids=["riposte"]  # Only 1 talent
        )
    assert "at least 2 items" in str(exc_info.value)
    
    print("✅ Invalid character data correctly rejected by schemas")


def test_three_character_archetypes():
    """Test creating characters for each path"""
    
    # Blade Warrior
    blade_char = CharacterCreate(
        name="Kael the Blade",
        origin_id="veteran",
        path_id="blade",
        attributes=AttributeScores(might=6, agility=4, wits=3, presence=2),
        skills=SkillsDict(blade=8, brawl=4, survival=4),
        talent_ids=["riposte", "weapon_master"]
    )
    blade_hp = calculate_max_hp(blade_char.attributes.might)
    blade_focus = calculate_max_focus(blade_char.attributes.wits, blade_char.attributes.presence)
    
    # Shadow Rogue
    shadow_char = CharacterCreate(
        name="Vex the Shadow",
        origin_id="street_urchin",
        path_id="shadow",
        attributes=AttributeScores(might=2, agility=6, wits=4, presence=3),
        skills=SkillsDict(sneak=8, bow=4, insight=4),
        talent_ids=["smoke_step", "backstab"]
    )
    shadow_hp = calculate_max_hp(shadow_char.attributes.might)
    shadow_focus = calculate_max_focus(shadow_char.attributes.wits, shadow_char.attributes.presence)
    
    # Mystic Caster
    mystic_char = CharacterCreate(
        name="Lyra the Mystic",
        origin_id="acolyte",
        path_id="mystic",
        attributes=AttributeScores(might=2, agility=3, wits=6, presence=4),
        skills=SkillsDict(channel=8, lore=4, insight=4),
        talent_ids=["quick_ritual", "ward"]
    )
    mystic_hp = calculate_max_hp(mystic_char.attributes.might)
    mystic_focus = calculate_max_focus(mystic_char.attributes.wits, mystic_char.attributes.presence)
    
    print("\n✅ Three character archetypes created:")
    print(f"   Blade: {blade_char.name} - HP:{blade_hp}, Focus:{blade_focus}")
    print(f"   Shadow: {shadow_char.name} - HP:{shadow_hp}, Focus:{shadow_focus}")
    print(f"   Mystic: {mystic_char.name} - HP:{mystic_hp}, Focus:{mystic_focus}")
    
    # Verify different playstyles
    assert blade_hp > shadow_hp, "Blade should have more HP than Shadow"
    assert blade_hp > mystic_hp, "Blade should have more HP than Mystic"
    assert mystic_focus > blade_focus, "Mystic should have more Focus than Blade"
    assert mystic_focus > shadow_focus, "Mystic should have more Focus than Shadow"


if __name__ == "__main__":
    print("=" * 60)
    print("Integration Test: Rules Engine + Character Schemas")
    print("=" * 60)
    print()
    
    test_valid_character_creation_with_schemas()
    print()
    test_invalid_character_schemas()
    print()
    test_three_character_archetypes()
    print()
    print("=" * 60)
    print("✅ All integration tests passed!")
    print("=" * 60)
