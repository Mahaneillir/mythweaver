"""
Unit tests for the rules engine
"""
import pytest
from app.services.rules_engine import (
    roll_d12,
    calculate_attribute_bonus,
    calculate_skill_rank,
    perform_check,
    calculate_max_hp,
    calculate_max_focus,
    calculate_inventory_slots,
    validate_character_creation,
    validate_attribute_allocation,
    EdgeType,
    Outcome,
    ValidationError
)


class TestDiceRolls:
    """Test basic dice rolling"""
    
    def test_roll_d12_range(self):
        """Test that d12 rolls are in valid range"""
        for _ in range(100):
            roll = roll_d12()
            assert 1 <= roll <= 12, f"Roll {roll} out of range"
    
    def test_roll_d12_distribution(self):
        """Test that d12 produces varied results"""
        rolls = [roll_d12() for _ in range(1000)]
        unique_values = set(rolls)
        # Should have hit most values with 1000 rolls
        assert len(unique_values) >= 10, "Not enough variance in dice rolls"


class TestBonusCalculations:
    """Test attribute and skill bonus calculations"""
    
    def test_attribute_bonus_calculation(self):
        """Test EAB = score // 2"""
        assert calculate_attribute_bonus(0) == 0
        assert calculate_attribute_bonus(1) == 0
        assert calculate_attribute_bonus(2) == 1
        assert calculate_attribute_bonus(3) == 1
        assert calculate_attribute_bonus(6) == 3
        assert calculate_attribute_bonus(10) == 5
        assert calculate_attribute_bonus(20) == 10
    
    def test_skill_rank_calculation(self):
        """Test SR = score // 4"""
        assert calculate_skill_rank(0) == 0
        assert calculate_skill_rank(3) == 0
        assert calculate_skill_rank(4) == 1
        assert calculate_skill_rank(7) == 1
        assert calculate_skill_rank(8) == 2
        assert calculate_skill_rank(12) == 3
        assert calculate_skill_rank(20) == 5


class TestCheckResolution:
    """Test check resolution logic"""
    
    def test_perform_check_basic(self):
        """Test basic check without edge"""
        # Set seed for predictable testing
        result = perform_check(
            attribute_score=6,  # EAB = 3
            skill_score=8,      # SR = 2
            difficulty=10,
            edge=EdgeType.NONE,
            situational_modifier=0
        )
        
        assert result.attribute_bonus == 3
        assert result.skill_rank == 2
        assert len(result.dice_rolls) == 1
        assert 1 <= result.dice_rolls[0] <= 12
        assert result.edge_type == EdgeType.NONE
    
    def test_perform_check_with_advantage(self):
        """Test check with advantage (roll 2, keep higher)"""
        result = perform_check(
            attribute_score=4,
            skill_score=4,
            difficulty=10,
            edge=EdgeType.ADVANTAGE
        )
        
        assert len(result.dice_rolls) == 2
        # Used the higher roll
        assert result.total >= (max(result.dice_rolls) + result.attribute_bonus + result.skill_rank)
    
    def test_perform_check_with_disadvantage(self):
        """Test check with disadvantage (roll 2, keep lower)"""
        result = perform_check(
            attribute_score=4,
            skill_score=4,
            difficulty=10,
            edge=EdgeType.DISADVANTAGE
        )
        
        assert len(result.dice_rolls) == 2
        # Used the lower roll
        dice_result = min(result.dice_rolls)
        expected_total = dice_result + result.attribute_bonus + result.skill_rank
        assert result.total == expected_total
    
    def test_check_outcomes(self):
        """Test outcome classification"""
        # Strong Success (margin >= 5)
        result = perform_check(6, 8, 5, EdgeType.NONE, 0)
        # Min: 1+3+2 = 6, Max: 12+3+2 = 17
        # Will sometimes be strong success
        
        # Run multiple checks to test outcome distribution
        outcomes = []
        for _ in range(100):
            r = perform_check(6, 8, 10, EdgeType.NONE, 0)
            outcomes.append(r.outcome)
        
        # Should have variety of outcomes
        unique_outcomes = set(outcomes)
        assert len(unique_outcomes) >= 2, "Not enough outcome variety"
    
    def test_margin_calculation(self):
        """Test that margin is correctly calculated"""
        result = perform_check(6, 8, 10, EdgeType.NONE, 0)
        assert result.margin == result.total - result.difficulty


class TestDerivedStats:
    """Test derived stat calculations"""
    
    def test_max_hp_calculation(self):
        """Test HP = 8 + (might * 2)"""
        assert calculate_max_hp(0) == 8
        assert calculate_max_hp(3) == 14
        assert calculate_max_hp(6) == 20
        assert calculate_max_hp(10) == 28
    
    def test_max_focus_calculation(self):
        """Test Focus = 4 + wits + presence"""
        assert calculate_max_focus(0, 0) == 4
        assert calculate_max_focus(3, 2) == 9
        assert calculate_max_focus(6, 4) == 14
        assert calculate_max_focus(10, 10) == 24
    
    def test_inventory_slots_calculation(self):
        """Test Inventory = 8 + might"""
        assert calculate_inventory_slots(0) == 8
        assert calculate_inventory_slots(3) == 11
        assert calculate_inventory_slots(6) == 14


class TestCharacterValidation:
    """Test character creation validation"""
    
    def test_valid_character(self):
        """Test that valid character passes validation"""
        attributes = {
            'might': 6,
            'agility': 4,
            'wits': 3,
            'presence': 2
        }
        skills = {
            'Blade': 8, 'Bow': 0, 'Brawl': 0,
            'Sneak': 4, 'Survival': 0, 'Lore': 0,
            'Craft': 0, 'Influence': 0, 'Insight': 4,
            'Channel': 0
        }
        talents = [
            {'name': 'Riposte', 'requirements': {'path': 'blade'}},
            {'name': 'Shield Ally', 'requirements': {'path': 'blade'}}
        ]
        
        assert validate_character_creation(attributes, skills, talents, 'blade') is True
    
    def test_invalid_attribute_sum(self):
        """Test that wrong attribute sum fails"""
        attributes = {
            'might': 8,  # Sum = 17, should be 15
            'agility': 4,
            'wits': 3,
            'presence': 2
        }
        skills = {
            'Blade': 8, 'Bow': 0, 'Brawl': 0,
            'Sneak': 4, 'Survival': 0, 'Lore': 0,
            'Craft': 0, 'Influence': 0, 'Insight': 4,
            'Channel': 0
        }
        talents = [
            {'name': 'Riposte', 'requirements': {'path': 'blade'}},
            {'name': 'Shield Ally', 'requirements': {'path': 'blade'}}
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_character_creation(attributes, skills, talents, 'blade')
        assert "sum to 15" in str(exc_info.value)
    
    def test_invalid_skill_count(self):
        """Test that wrong number of skills fails"""
        attributes = {
            'might': 6,
            'agility': 4,
            'wits': 3,
            'presence': 2
        }
        skills = {
            'Blade': 8, 'Bow': 4, 'Brawl': 0,  # 4 skills selected
            'Sneak': 4, 'Survival': 4, 'Lore': 0,
            'Craft': 0, 'Influence': 0, 'Insight': 0,
            'Channel': 0
        }
        talents = [
            {'name': 'Riposte', 'requirements': {'path': 'blade'}},
            {'name': 'Shield Ally', 'requirements': {'path': 'blade'}}
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_character_creation(attributes, skills, talents, 'blade')
        assert "exactly 3 starting skills" in str(exc_info.value)
    
    def test_invalid_talent_count(self):
        """Test that wrong number of talents fails"""
        attributes = {
            'might': 6,
            'agility': 4,
            'wits': 3,
            'presence': 2
        }
        skills = {
            'Blade': 8, 'Bow': 0, 'Brawl': 0,
            'Sneak': 4, 'Survival': 0, 'Lore': 0,
            'Craft': 0, 'Influence': 0, 'Insight': 4,
            'Channel': 0
        }
        talents = [
            {'name': 'Riposte', 'requirements': {'path': 'blade'}}
        ]  # Only 1 talent
        
        with pytest.raises(ValidationError) as exc_info:
            validate_character_creation(attributes, skills, talents, 'blade')
        assert "exactly 2 starting talents" in str(exc_info.value)
    
    def test_attribute_out_of_range(self):
        """Test that out-of-range attributes fail"""
        attributes = {
            'might': 25,  # Over 20
            'agility': 4,
            'wits': 3,
            'presence': 2
        }
        skills = {
            'Blade': 8, 'Bow': 0, 'Brawl': 0,
            'Sneak': 4, 'Survival': 0, 'Lore': 0,
            'Craft': 0, 'Influence': 0, 'Insight': 4,
            'Channel': 0
        }
        talents = [
            {'name': 'Riposte', 'requirements': {'path': 'blade'}},
            {'name': 'Shield Ally', 'requirements': {'path': 'blade'}}
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            validate_character_creation(attributes, skills, talents, 'blade')
        assert "must be 0-20" in str(exc_info.value)


class TestAttributeAllocationValidation:
    """Test quick attribute allocation validation for UI"""
    
    def test_valid_allocation(self):
        """Test valid allocation returns True"""
        attributes = {'might': 6, 'agility': 4, 'wits': 3, 'presence': 2}
        assert validate_attribute_allocation(attributes) is True
    
    def test_invalid_sum(self):
        """Test invalid sum returns False"""
        attributes = {'might': 8, 'agility': 4, 'wits': 3, 'presence': 2}
        assert validate_attribute_allocation(attributes) is False
    
    def test_missing_attribute(self):
        """Test missing attribute returns False"""
        attributes = {'might': 6, 'agility': 4, 'wits': 3}
        assert validate_attribute_allocation(attributes) is False
