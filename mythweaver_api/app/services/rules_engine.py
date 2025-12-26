"""
Mythweaver Rules Engine
Handles dice rolls, checks, validation, and stat calculations
"""
import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List


class EdgeType(Enum):
    """Edge/Trouble modifiers for checks"""
    NONE = "none"
    ADVANTAGE = "advantage"  # Roll 2d12, keep higher
    DISADVANTAGE = "disadvantage"  # Roll 2d12, keep lower


class Outcome(Enum):
    """Check outcome categories"""
    FAILURE = "failure"  # Missed by 3+
    NEAR_MISS = "near_miss"  # Missed by 1-2
    SUCCESS = "success"  # Met or exceeded by 0-4
    STRONG_SUCCESS = "strong_success"  # Exceeded by 5+


@dataclass
class CheckResult:
    """Result of a check with full breakdown"""
    total: int
    difficulty: int
    margin: int  # total - difficulty
    outcome: Outcome
    dice_rolls: List[int]  # Raw dice rolls (1 or 2 if edge/trouble)
    attribute_bonus: int
    skill_rank: int
    situational_modifier: int
    edge_type: EdgeType


# Core Dice Logic

def roll_d12() -> int:
    """Roll a single d12 (1-12)"""
    return random.randint(1, 12)


def calculate_attribute_bonus(score: int) -> int:
    """
    Calculate Effective Attribute Bonus (EAB)
    EAB = floor(score / 2)
    """
    return score // 2


def calculate_skill_rank(score: int) -> int:
    """
    Calculate Skill Rank (SR)
    SR = floor(score / 4)
    """
    return score // 4


# Check Resolution

def perform_check(
    attribute_score: int,
    skill_score: int,
    difficulty: int,
    edge: EdgeType = EdgeType.NONE,
    situational_modifier: int = 0
) -> CheckResult:
    """
    Perform a check against a difficulty.
    
    Args:
        attribute_score: Character's attribute score (0-20)
        skill_score: Character's skill score (0-20)
        difficulty: Target difficulty (typically 7-15)
        edge: Advantage/disadvantage/none
        situational_modifier: Additional +/- modifier
    
    Returns:
        CheckResult with full breakdown
    """
    # Calculate bonuses
    attribute_bonus = calculate_attribute_bonus(attribute_score)
    skill_rank = calculate_skill_rank(skill_score)
    
    # Roll dice based on edge
    dice_rolls = []
    if edge == EdgeType.ADVANTAGE:
        roll1 = roll_d12()
        roll2 = roll_d12()
        dice_rolls = [roll1, roll2]
        dice_result = max(roll1, roll2)
    elif edge == EdgeType.DISADVANTAGE:
        roll1 = roll_d12()
        roll2 = roll_d12()
        dice_rolls = [roll1, roll2]
        dice_result = min(roll1, roll2)
    else:  # NONE
        dice_result = roll_d12()
        dice_rolls = [dice_result]
    
    # Calculate total
    total = dice_result + attribute_bonus + skill_rank + situational_modifier
    margin = total - difficulty
    
    # Determine outcome
    if margin >= 5:
        outcome = Outcome.STRONG_SUCCESS
    elif margin >= 0:
        outcome = Outcome.SUCCESS
    elif margin >= -2:
        outcome = Outcome.NEAR_MISS
    else:
        outcome = Outcome.FAILURE
    
    return CheckResult(
        total=total,
        difficulty=difficulty,
        margin=margin,
        outcome=outcome,
        dice_rolls=dice_rolls,
        attribute_bonus=attribute_bonus,
        skill_rank=skill_rank,
        situational_modifier=situational_modifier,
        edge_type=edge
    )


# Derived Stats Calculation

def calculate_max_hp(might_score: int) -> int:
    """
    Calculate maximum HP
    Formula: 8 + (might_score * 2)
    """
    return 8 + (might_score * 2)


def calculate_max_focus(wits_score: int, presence_score: int) -> int:
    """
    Calculate maximum Focus
    Formula: 4 + wits + presence
    """
    return 4 + wits_score + presence_score


def calculate_inventory_slots(might_score: int) -> int:
    """
    Calculate inventory capacity
    Formula: 8 + might
    """
    return 8 + might_score


# Character Creation Validation

class ValidationError(Exception):
    """Raised when character creation validation fails"""
    pass


def validate_character_creation(
    attributes: Dict[str, int],
    skills: Dict[str, int],
    talents: List[Dict],
    path_id: str
) -> bool:
    """
    Validate character creation data.
    
    Args:
        attributes: Dict with might, agility, wits, presence
        skills: Dict with all 10 skill scores
        talents: List of talent dicts with 'name' and 'requirements'
        path_id: Character's chosen path
    
    Returns:
        True if valid
    
    Raises:
        ValidationError with specific reason
    """
    # Validate attributes
    required_attrs = ['might', 'agility', 'wits', 'presence']
    for attr in required_attrs:
        if attr not in attributes:
            raise ValidationError(f"Missing attribute: {attr}")
        
        score = attributes[attr]
        if not 0 <= score <= 20:
            raise ValidationError(f"Attribute {attr} must be 0-20, got {score}")
    
    # Check attributes sum to 15 (6+4+3+2)
    attr_total = sum(attributes[attr] for attr in required_attrs)
    if attr_total != 15:
        raise ValidationError(f"Attributes must sum to 15, got {attr_total}")
    
    # Validate skills
    required_skills = ['Blade', 'Bow', 'Brawl', 'Sneak', 'Survival', 
                      'Lore', 'Craft', 'Influence', 'Insight', 'Channel']
    
    for skill in required_skills:
        if skill not in skills:
            raise ValidationError(f"Missing skill: {skill}")
        
        score = skills[skill]
        if not 0 <= score <= 20:
            raise ValidationError(f"Skill {skill} must be 0-20, got {score}")
    
    # Check exactly 3 starting skills selected (non-zero)
    selected_skills = [skill for skill, score in skills.items() if score > 0]
    if len(selected_skills) != 3:
        raise ValidationError(f"Must select exactly 3 starting skills, got {len(selected_skills)}")
    
    # Validate talents
    if len(talents) != 2:
        raise ValidationError(f"Must select exactly 2 starting talents, got {len(talents)}")
    
    # Check talent validity (path requirements)
    # Note: This is simplified validation. Full validation would use game_data_service
    for talent in talents:
        if 'name' not in talent:
            raise ValidationError(f"Talent missing 'name' field")
    
    return True


def validate_attribute_allocation(attributes: Dict[str, int]) -> bool:
    """
    Quick validation for attribute allocation UI
    Returns True if allocation is valid for submission
    """
    try:
        required = ['might', 'agility', 'wits', 'presence']
        if not all(attr in attributes for attr in required):
            return False
        
        total = sum(attributes[attr] for attr in required)
        if total != 15:
            return False
        
        # Check all in valid range
        for attr in required:
            if not 0 <= attributes[attr] <= 20:
                return False
        
        return True
    except:
        return False
