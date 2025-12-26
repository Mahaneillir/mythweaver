"""
Demonstration of the Mythweaver Rules Engine
Shows example usage of all core functions
"""
from app.services.rules_engine import (
    roll_d12,
    calculate_attribute_bonus,
    calculate_skill_rank,
    perform_check,
    calculate_max_hp,
    calculate_max_focus,
    calculate_inventory_slots,
    validate_character_creation,
    EdgeType,
    Outcome
)


def demo_dice_rolls():
    """Demonstrate dice rolling"""
    print("=== Dice Rolling Demo ===")
    rolls = [roll_d12() for _ in range(5)]
    print(f"5 d12 rolls: {rolls}")
    print()


def demo_bonus_calculations():
    """Demonstrate attribute and skill bonus calculations"""
    print("=== Bonus Calculations Demo ===")
    
    might = 6
    blade_skill = 8
    
    eab = calculate_attribute_bonus(might)
    sr = calculate_skill_rank(blade_skill)
    
    print(f"Might {might} → EAB +{eab}")
    print(f"Blade Skill {blade_skill} → Rank {sr}")
    print()


def demo_check_resolution():
    """Demonstrate check resolution"""
    print("=== Check Resolution Demo ===")
    
    # Example: Character with Might 6, Blade 8 attacking (difficulty 11)
    result = perform_check(
        attribute_score=6,
        skill_score=8,
        difficulty=11,
        edge=EdgeType.NONE,
        situational_modifier=0
    )
    
    print(f"Attack Check:")
    print(f"  Dice Roll: {result.dice_rolls[0]}")
    print(f"  + Might Bonus: +{result.attribute_bonus}")
    print(f"  + Blade Rank: +{result.skill_rank}")
    print(f"  = Total: {result.total} vs Difficulty {result.difficulty}")
    print(f"  Margin: {result.margin:+d}")
    print(f"  Outcome: {result.outcome.value.upper()}")
    print()
    
    # Example with advantage
    result_adv = perform_check(
        attribute_score=4,
        skill_score=4,
        difficulty=12,
        edge=EdgeType.ADVANTAGE
    )
    
    print(f"Stealth Check with Advantage:")
    print(f"  Dice Rolls: {result_adv.dice_rolls} (kept {max(result_adv.dice_rolls)})")
    print(f"  Total: {result_adv.total} vs Difficulty {result_adv.difficulty}")
    print(f"  Outcome: {result_adv.outcome.value.upper()}")
    print()


def demo_derived_stats():
    """Demonstrate derived stat calculations"""
    print("=== Derived Stats Demo ===")
    
    might = 6
    wits = 3
    presence = 2
    
    hp = calculate_max_hp(might)
    focus = calculate_max_focus(wits, presence)
    inventory = calculate_inventory_slots(might)
    
    print(f"Character with Might {might}, Wits {wits}, Presence {presence}:")
    print(f"  Max HP: {hp}")
    print(f"  Max Focus: {focus}")
    print(f"  Inventory Slots: {inventory}")
    print()


def demo_character_validation():
    """Demonstrate character validation"""
    print("=== Character Validation Demo ===")
    
    # Valid character
    valid_attrs = {'might': 6, 'agility': 4, 'wits': 3, 'presence': 2}
    valid_skills = {
        'Blade': 8, 'Bow': 0, 'Brawl': 0,
        'Sneak': 4, 'Survival': 0, 'Lore': 0,
        'Craft': 0, 'Influence': 0, 'Insight': 4, 'Channel': 0
    }
    valid_talents = [
        {'name': 'Riposte', 'requirements': {'path': 'blade'}},
        {'name': 'Shield Ally', 'requirements': {'path': 'blade'}}
    ]
    
    try:
        validate_character_creation(valid_attrs, valid_skills, valid_talents, 'blade')
        print("✅ Valid character passed validation")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    # Invalid character (wrong attribute sum)
    invalid_attrs = {'might': 8, 'agility': 4, 'wits': 3, 'presence': 2}
    
    try:
        validate_character_creation(invalid_attrs, valid_skills, valid_talents, 'blade')
        print("✅ Invalid character passed (shouldn't happen)")
    except Exception as e:
        print(f"✅ Invalid character correctly rejected: {e}")
    print()


def demo_combat_scenario():
    """Demonstrate a complete combat scenario"""
    print("=== Combat Scenario Demo ===")
    print("A Blade warrior faces a bandit guard...")
    print()
    
    # Warrior stats
    might = 6  # EAB +3
    blade = 8  # Rank 2
    
    print(f"Warrior: Might {might} (+{calculate_attribute_bonus(might)}), Blade {blade} (Rank {calculate_skill_rank(blade)})")
    print()
    
    # Round 1: Normal attack
    print("Round 1: Warrior attacks (difficulty 11)")
    result1 = perform_check(might, blade, 11)
    print(f"  Roll: {result1.dice_rolls[0]} + {result1.attribute_bonus} + {result1.skill_rank} = {result1.total}")
    print(f"  Result: {result1.outcome.value.upper()}")
    
    if result1.outcome in [Outcome.SUCCESS, Outcome.STRONG_SUCCESS]:
        damage = 6 + calculate_attribute_bonus(might)
        print(f"  ⚔️ Hit! Damage: {damage}")
    else:
        print(f"  ❌ Miss!")
    print()
    
    # Round 2: Attack with advantage (flanking)
    print("Round 2: Warrior attacks with ally flanking (advantage)")
    result2 = perform_check(might, blade, 11, EdgeType.ADVANTAGE)
    print(f"  Rolls: {result2.dice_rolls} → kept {max(result2.dice_rolls)}")
    print(f"  Total: {result2.total} vs {result2.difficulty}")
    print(f"  Result: {result2.outcome.value.upper()}")
    
    if result2.outcome in [Outcome.SUCCESS, Outcome.STRONG_SUCCESS]:
        damage = 6 + calculate_attribute_bonus(might)
        if result2.outcome == Outcome.STRONG_SUCCESS:
            damage += 3  # Bonus damage on strong success
        print(f"  ⚔️ Hit! Damage: {damage}")
    print()


if __name__ == "__main__":
    print("╔═══════════════════════════════════════╗")
    print("║   Mythweaver Rules Engine Demo       ║")
    print("╚═══════════════════════════════════════╝")
    print()
    
    demo_dice_rolls()
    demo_bonus_calculations()
    demo_check_resolution()
    demo_derived_stats()
    demo_character_validation()
    demo_combat_scenario()
    
    print("=" * 50)
    print("✅ All rules engine functions demonstrated!")
    print("=" * 50)
