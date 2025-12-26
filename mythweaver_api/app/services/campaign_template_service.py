"""
Campaign Template Service
Loads and manages campaign templates
"""
import json
from pathlib import Path
from typing import Dict, Optional
from functools import lru_cache


TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "campaign_templates"


@lru_cache(maxsize=10)
def load_campaign_template(template_id: str) -> Optional[Dict]:
    """
    Load a campaign template by ID
    
    Args:
        template_id: Template identifier (e.g., "broken_kingdom")
    
    Returns:
        Template dictionary or None if not found
    """
    template_path = TEMPLATES_DIR / f"{template_id}.json"
    
    if not template_path.exists():
        return None
    
    with open(template_path, 'r') as f:
        return json.load(f)


def get_opening_narration(template_id: str, origin_id: str) -> str:
    """
    Generate opening narration for a campaign based on template and character origin
    
    Args:
        template_id: Campaign template ID
        origin_id: Character origin ID (e.g., "street_urchin")
    
    Returns:
        Formatted opening narration text
    """
    template = load_campaign_template(template_id)
    if not template:
        raise ValueError(f"Template '{template_id}' not found")
    
    opening_scene = template.get("opening_scene", {})
    narration_template = opening_scene.get("narration_template", "")
    origin_contexts = opening_scene.get("origin_context", {})
    
    # Get origin-specific context
    origin_context = origin_contexts.get(origin_id, "You've been on the road, searching for purpose.")
    
    # Replace placeholder with origin context
    narration = narration_template.replace("{origin_context}", origin_context)
    
    return narration


def get_suggested_actions(template_id: str) -> list:
    """
    Get suggested starting actions for a campaign
    
    Args:
        template_id: Campaign template ID
    
    Returns:
        List of suggested action strings
    """
    template = load_campaign_template(template_id)
    if not template:
        return ["Look around", "Wait and observe"]
    
    opening_scene = template.get("opening_scene", {})
    return opening_scene.get("suggested_actions", [])


def get_starting_location(template_id: str) -> str:
    """
    Get the starting location for a campaign
    
    Args:
        template_id: Campaign template ID
    
    Returns:
        Starting location name
    """
    template = load_campaign_template(template_id)
    if not template:
        return "Unknown Location"
    
    return template.get("starting_location", "Unknown Location")


def get_template_info(template_id: str) -> Dict:
    """
    Get basic template information without full details
    
    Args:
        template_id: Campaign template ID
    
    Returns:
        Dict with name, description, and basic info
    """
    template = load_campaign_template(template_id)
    if not template:
        return {
            "template_id": template_id,
            "name": "Unknown Campaign",
            "description": "Template not found"
        }
    
    return {
        "template_id": template.get("template_id"),
        "name": template.get("name"),
        "description": template.get("description"),
        "starting_location": template.get("starting_location")
    }


def validate_template(template_id: str) -> bool:
    """
    Check if a campaign template exists and is valid
    
    Args:
        template_id: Template identifier
    
    Returns:
        True if template exists and has required fields
    """
    template = load_campaign_template(template_id)
    if not template:
        return False
    
    required_fields = ["template_id", "name", "opening_scene", "starting_location"]
    return all(field in template for field in required_fields)
