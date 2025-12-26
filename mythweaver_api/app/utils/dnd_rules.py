import random
from typing import Dict, List, Any, Tuple
import math


class DnDRules:
    """D&D 5e SRD rules implementation for hidden mechanics"""
    
    def __init__(self):
        self.ability_modifier_map = {
            1: -5, 2: -4, 3: -4, 4: -3, 5: -3, 6: -2, 7: -2, 8: -1, 9: -1, 10: 0,
            11: 0, 12: 1, 13: 1, 14: 2, 15: 2, 16: 3, 17: 3, 18: 4, 19: 4, 20: 5
        }
    
    def get_ability_modifier(self, ability_score: int) -> int:
        """Get ability modifier from score"""
        return self.ability_modifier_map.get(ability_score, 0)
    
    def get_proficiency_bonus(self, level: int) -> int:
        """Get proficiency bonus by character level"""
        if level >= 17:
            return 6
        elif level >= 13:
            return 5
        elif level >= 9:
            return 4
        elif level >= 5:
            return 3
        else:
            return 2
    
    def roll_dice(self, dice_type: str, num_dice: int = 1, modifier: int = 0) -> Dict[str, Any]:
        """Roll dice and return results"""
        die_value = int(dice_type.replace('d', ''))
        rolls = [random.randint(1, die_value) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        
        return {
            "type": f"{num_dice}{dice_type}" if num_dice > 1 else dice_type,
            "rolls": rolls,
            "modifier": modifier,
            "total": total,
            "success": total >= 10 if dice_type == "d20" else True  # Default DC 10 for ability checks
        }
    
    def make_ability_check(
        self, 
        ability_score: int, 
        proficiency_bonus: int = 0, 
        difficulty_class: int = 15,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> Dict[str, Any]:
        """Make an ability check with optional advantage/disadvantage"""
        modifier = self.get_ability_modifier(ability_score) + proficiency_bonus
        
        if advantage and not disadvantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll_result = max(roll1, roll2)
        elif disadvantage and not advantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            roll_result = min(roll1, roll2)
        else:
            roll_result = random.randint(1, 20)
        
        total = roll_result + modifier
        success = total >= difficulty_class
        
        return {
            "type": "d20",
            "result": roll_result,
            "modifier": modifier,
            "total": total,
            "dc": difficulty_class,
            "success": success,
            "advantage": advantage,
            "disadvantage": disadvantage
        }
    
    def calculate_armor_class(self, dexterity: int, armor_type: str = "leather_armor") -> int:
        """Calculate AC based on armor and dexterity"""
        dex_mod = self.get_ability_modifier(dexterity)
        
        armor_ac = {
            "leather_armor": 11,
            "chain_mail": 16,
            "plate_armor": 18,
            "no_armor": 10
        }
        
        base_ac = armor_ac.get(armor_type, 10)
        
        if armor_type in ["leather_armor", "no_armor"]:
            return base_ac + dex_mod
        elif armor_type == "chain_mail":
            return base_ac + min(dex_mod, 2)  # Max +2 dex
        else:
            return base_ac  # Plate armor ignores dex
    
    def calculate_armor_class_from_equipment(self, dexterity: int, equipment: Dict[str, Any]) -> int:
        """Calculate AC from current equipment"""
        armor = equipment.get("armor", "no_armor")
        return self.calculate_armor_class(dexterity, armor)
    
    def calculate_saving_throws(
        self, 
        stats: Dict[str, int], 
        character_class: str, 
        proficiency_bonus: int
    ) -> Dict[str, int]:
        """Calculate saving throw modifiers"""
        saving_throws = {}
        
        # Class proficiencies
        class_proficiencies = {
            "rogue": ["dexterity", "intelligence"],
            "fighter": ["strength", "constitution"],
            "wizard": ["intelligence", "wisdom"],
            "cleric": ["wisdom", "charisma"]
        }
        
        proficient_saves = class_proficiencies.get(character_class, [])
        
        for ability, score in stats.items():
            modifier = self.get_ability_modifier(score)
            if ability in proficient_saves:
                modifier += proficiency_bonus
            saving_throws[ability] = modifier
        
        return saving_throws
    
    def calculate_starting_health(self, character_class: str, constitution: int) -> Dict[str, int]:
        """Calculate starting health"""
        class_hit_dice = {
            "rogue": 8,
            "fighter": 10,
            "wizard": 6,
            "cleric": 8
        }
        
        hit_die = class_hit_dice.get(character_class, 8)
        con_mod = self.get_ability_modifier(constitution)
        starting_hp = hit_die + con_mod
        
        return {
            "current": starting_hp,
            "maximum": starting_hp,
            "temporary": 0
        }
    
    def get_starting_equipment(self, character_class: str, background: str) -> Tuple[List[Dict], Dict]:
        """Get starting equipment based on class and background"""
        
        # Base equipment by class
        class_equipment = {
            "rogue": [
                {"item": "shortsword", "quantity": 1, "type": "weapon", 
                 "properties": {"damage": "1d6", "finesse": True, "light": True}},
                {"item": "dagger", "quantity": 2, "type": "weapon",
                 "properties": {"damage": "1d4", "finesse": True, "light": True, "thrown": True}},
                {"item": "thieves_tools", "quantity": 1, "type": "misc", "properties": {"tool": True}},
                {"item": "leather_armor", "quantity": 1, "type": "armor", 
                 "properties": {"ac": 11, "dex_bonus": True}},
                {"item": "gold_pieces", "quantity": 15, "type": "misc", "properties": {"currency": True}}
            ]
        }
        
        # Equipment configuration
        equipment_config = {
            "armor": "leather_armor",
            "weapons": {
                "primary": "shortsword",
                "secondary": "dagger"
            }
        }
        
        inventory = class_equipment.get(character_class, [])
        
        return inventory, equipment_config
    
    def get_level_up_benefits(self, character_class: str, current_level: int, new_level: int) -> Dict[str, Any]:
        """Get benefits for leveling up"""
        
        benefits = {
            "new_features": [],
            "skill_improvements": [],
            "ability_score_improvements": []
        }
        
        # Level 2 rogue gets Cunning Action
        if character_class == "rogue" and new_level == 2:
            benefits["new_features"].append({
                "name": "Cunning Action",
                "description": "Take Dash, Disengage, or Hide action as bonus action"
            })
            benefits["skill_improvements"].append("investigation")  # Example improvement
        
        return benefits
    
    def calculate_experience_for_level(self, level: int) -> int:
        """Calculate XP required for level"""
        xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
            85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        
        if level <= 20:
            return xp_thresholds[level - 1]
        return xp_thresholds[-1]