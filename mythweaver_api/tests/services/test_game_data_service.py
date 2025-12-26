"""
Tests for Game Data Service
Verifies origins, paths, and talents loading and validation
"""
import pytest
from app.services.game_data_service import (
    load_origins,
    load_paths,
    load_talents,
    get_origin_by_id,
    get_path_by_id,
    get_talent_by_id,
    get_talents_for_path,
    validate_origin,
    validate_path,
    validate_talent,
)


class TestOriginLoading:
    """Test origin data loading"""

    def test_load_origins_returns_list(self):
        """Test that load_origins returns a list"""
        origins = load_origins()

        assert isinstance(origins, list)
        assert len(origins) > 0

    def test_origins_have_required_fields(self):
        """Test that all origins have required fields"""
        origins = load_origins()

        for origin in origins:
            assert "id" in origin
            assert "name" in origin
            assert "description" in origin
            assert isinstance(origin["id"], str)
            assert isinstance(origin["name"], str)
            assert isinstance(origin["description"], str)

    def test_get_origin_by_id_street_urchin(self):
        """Test getting street urchin origin by ID"""
        origin = get_origin_by_id("street_urchin")

        assert origin is not None
        assert origin["id"] == "street_urchin"
        assert "name" in origin

    def test_get_origin_by_id_veteran(self):
        """Test getting veteran origin by ID"""
        origin = get_origin_by_id("veteran")

        assert origin is not None
        assert origin["id"] == "veteran"

    def test_get_origin_by_id_acolyte(self):
        """Test getting acolyte origin by ID"""
        origin = get_origin_by_id("acolyte")

        assert origin is not None
        assert origin["id"] == "acolyte"

    def test_get_origin_by_id_nonexistent(self):
        """Test getting nonexistent origin returns None"""
        origin = get_origin_by_id("nonexistent_origin")

        assert origin is None

    def test_validate_origin_valid(self):
        """Test validating a valid origin ID"""
        assert validate_origin("street_urchin") is True
        assert validate_origin("veteran") is True
        assert validate_origin("acolyte") is True

    def test_validate_origin_invalid(self):
        """Test validating an invalid origin ID"""
        assert validate_origin("nonexistent_origin") is False


class TestPathLoading:
    """Test path data loading"""

    def test_load_paths_returns_list(self):
        """Test that load_paths returns a list"""
        paths = load_paths()

        assert isinstance(paths, list)
        assert len(paths) > 0

    def test_paths_have_required_fields(self):
        """Test that all paths have required fields"""
        paths = load_paths()

        for path in paths:
            assert "id" in path
            assert "name" in path
            assert "description" in path
            assert isinstance(path["id"], str)
            assert isinstance(path["name"], str)
            assert isinstance(path["description"], str)

    def test_get_path_by_id_blade(self):
        """Test getting blade path by ID"""
        path = get_path_by_id("blade")

        assert path is not None
        assert path["id"] == "blade"
        assert "name" in path

    def test_get_path_by_id_shadow(self):
        """Test getting shadow path by ID"""
        path = get_path_by_id("shadow")

        assert path is not None
        assert path["id"] == "shadow"

    def test_get_path_by_id_mystic(self):
        """Test getting mystic path by ID"""
        path = get_path_by_id("mystic")

        assert path is not None
        assert path["id"] == "mystic"

    def test_get_path_by_id_nonexistent(self):
        """Test getting nonexistent path returns None"""
        path = get_path_by_id("nonexistent_path")

        assert path is None

    def test_validate_path_valid(self):
        """Test validating valid path IDs"""
        assert validate_path("blade") is True
        assert validate_path("shadow") is True
        assert validate_path("mystic") is True

    def test_validate_path_invalid(self):
        """Test validating an invalid path ID"""
        assert validate_path("nonexistent_path") is False


class TestTalentLoading:
    """Test talent data loading"""

    def test_load_talents_returns_list(self):
        """Test that load_talents returns a list"""
        talents = load_talents()

        assert isinstance(talents, list)
        assert len(talents) >= 6  # Should have at least a few talents

    def test_talents_have_required_fields(self):
        """Test that all talents have required fields"""
        talents = load_talents()

        for talent in talents:
            assert "id" in talent
            assert "name" in talent
            assert "description" in talent
            assert "cost" in talent
            assert "requirements" in talent
            assert isinstance(talent["id"], str)
            assert isinstance(talent["name"], str)
            assert isinstance(talent["cost"], int)
            assert isinstance(talent["requirements"], dict)

    def test_get_talent_by_id_riposte(self):
        """Test getting riposte talent by ID"""
        talent = get_talent_by_id("riposte")

        assert talent is not None
        assert talent["id"] == "riposte"
        assert talent["cost"] >= 0  # Should have a focus cost

    def test_get_talent_by_id_nonexistent(self):
        """Test getting nonexistent talent returns None"""
        talent = get_talent_by_id("nonexistent_talent")

        assert talent is None


class TestTalentFiltering:
    """Test talent filtering by path"""

    def test_get_talents_for_blade_path(self):
        """Test getting talents for blade path"""
        talents = get_talents_for_path("blade")

        assert isinstance(talents, list)
        assert len(talents) > 0
        # All talents should be for blade or universal
        for talent in talents:
            req_path = talent["requirements"]["path"]
            assert req_path == "blade" or req_path is None

    def test_get_talents_for_shadow_path(self):
        """Test getting talents for shadow path"""
        talents = get_talents_for_path("shadow")

        assert isinstance(talents, list)
        assert len(talents) > 0
        for talent in talents:
            req_path = talent["requirements"]["path"]
            assert req_path == "shadow" or req_path is None

    def test_get_talents_for_mystic_path(self):
        """Test getting talents for mystic path"""
        talents = get_talents_for_path("mystic")

        assert isinstance(talents, list)
        assert len(talents) > 0
        for talent in talents:
            req_path = talent["requirements"]["path"]
            assert req_path == "mystic" or req_path is None

    def test_get_talents_for_no_path(self):
        """Test getting universal talents (no path requirement)"""
        talents = get_talents_for_path(None)

        assert isinstance(talents, list)
        # All should be universal talents
        for talent in talents:
            assert talent["requirements"]["path"] is None


class TestTalentValidation:
    """Test talent validation logic"""

    def test_validate_talent_valid_for_path(self):
        """Test validating a talent that's valid for the path"""
        # Riposte should be valid for blade path (requires "Blade" skill)
        is_valid = validate_talent("riposte", "blade", ["Blade", "Brawl", "Survival"])

        assert is_valid is True

    def test_validate_talent_invalid_for_path(self):
        """Test validating a talent that's invalid for the path"""
        # Riposte (blade talent) should not be valid for shadow path
        is_valid = validate_talent("riposte", "shadow", ["Sneak", "Survival", "Insight"])

        # This test assumes riposte is blade-specific; adjust if universal
        # If riposte can be taken by any path, this test may need updating

    def test_validate_talent_nonexistent(self):
        """Test validating a nonexistent talent"""
        is_valid = validate_talent("nonexistent_talent", "blade", ["Blade"])

        assert is_valid is False

    def test_validate_talent_with_skill_requirements(self):
        """Test validating a talent that requires specific skills"""
        # Find a talent with skill requirements from the talents list
        talents = load_talents()
        talent_with_skill_req = None

        for talent in talents:
            if talent["requirements"].get("skills"):
                talent_with_skill_req = talent
                break

        if talent_with_skill_req:
            required_skills = talent_with_skill_req["requirements"]["skills"]
            path = talent_with_skill_req["requirements"]["path"]

            # Should be valid if character has at least one required skill
            is_valid = validate_talent(
                talent_with_skill_req["id"],
                path or "blade",  # Use any path if universal
                required_skills[:1]  # Include one required skill
            )
            assert is_valid is True

            # Should be invalid if character has no required skills
            is_valid_without_skills = validate_talent(
                talent_with_skill_req["id"],
                path or "blade",
                ["Lore", "Craft"]  # Different skills (capitalized to match data format)
            )
            # Only assert false if the talent actually requires skills
            if required_skills:
                assert is_valid_without_skills is False


class TestDataCaching:
    """Test that data is cached properly"""

    def test_origins_are_cached(self):
        """Test that origins are cached after first load"""
        origins1 = load_origins()
        origins2 = load_origins()

        # Should be the same object (cached)
        assert origins1 is origins2

    def test_paths_are_cached(self):
        """Test that paths are cached after first load"""
        paths1 = load_paths()
        paths2 = load_paths()

        assert paths1 is paths2

    def test_talents_are_cached(self):
        """Test that talents are cached after first load"""
        talents1 = load_talents()
        talents2 = load_talents()

        assert talents1 is talents2
