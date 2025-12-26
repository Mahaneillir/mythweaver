"""
Game Data Service
Loads and caches game data (origins, paths, talents) from JSON files
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache


DATA_DIR = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=1)
def load_origins() -> List[Dict]:
    """Load all available origins from origins.json"""
    origins_path = DATA_DIR / "origins.json"
    with open(origins_path, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_paths() -> List[Dict]:
    """Load all available paths from paths.json"""
    paths_path = DATA_DIR / "paths.json"
    with open(paths_path, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_talents() -> List[Dict]:
    """Load all available talents from talents.json"""
    talents_path = DATA_DIR / "talents.json"
    with open(talents_path, 'r') as f:
        return json.load(f)


def get_origin_by_id(origin_id: str) -> Optional[Dict]:
    """Get a specific origin by ID"""
    origins = load_origins()
    for origin in origins:
        if origin['id'] == origin_id:
            return origin
    return None


def get_path_by_id(path_id: str) -> Optional[Dict]:
    """Get a specific path by ID"""
    paths = load_paths()
    for path in paths:
        if path['id'] == path_id:
            return path
    return None


def get_talent_by_id(talent_id: str) -> Optional[Dict]:
    """Get a specific talent by ID"""
    talents = load_talents()
    for talent in talents:
        if talent['id'] == talent_id:
            return talent
    return None


def get_talents_for_path(path_id: Optional[str] = None) -> List[Dict]:
    """
    Get talents available for a specific path.
    If path_id is None, returns talents available to all paths.
    """
    talents = load_talents()
    if path_id is None:
        # Return talents with no path requirement
        return [t for t in talents if t['requirements']['path'] is None]
    else:
        # Return talents for this path OR universal talents
        return [
            t for t in talents
            if t['requirements']['path'] == path_id or t['requirements']['path'] is None
        ]


def validate_origin(origin_id: str) -> bool:
    """Check if origin ID is valid"""
    return get_origin_by_id(origin_id) is not None


def validate_path(path_id: str) -> bool:
    """Check if path ID is valid"""
    return get_path_by_id(path_id) is not None


def validate_talent(talent_id: str, path_id: str, skills: List[str]) -> bool:
    """
    Check if a talent is valid for the given path and skills.
    Returns True if the character can take this talent.
    """
    talent = get_talent_by_id(talent_id)
    if not talent:
        return False
    
    # Check path requirement
    required_path = talent['requirements']['path']
    if required_path is not None and required_path != path_id:
        return False
    
    # Check skill requirements
    required_skills = talent['requirements']['skills']
    if required_skills:
        # Character must have at least one of the required skills
        if not any(skill in skills for skill in required_skills):
            return False
    
    return True
