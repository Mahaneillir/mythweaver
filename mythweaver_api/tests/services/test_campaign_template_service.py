"""
Tests for Campaign Template Service
Verifies template loading, narration generation, and validation
"""
import pytest
from app.services.campaign_template_service import (
    load_campaign_template,
    get_opening_narration,
    get_suggested_actions,
    get_starting_location,
    get_template_info,
    validate_template,
)


class TestCampaignTemplateLoading:
    """Test campaign template loading functionality"""

    def test_load_broken_kingdom_template(self):
        """Test loading the default 'broken_kingdom' template"""
        template = load_campaign_template("broken_kingdom")

        assert template is not None
        assert template["template_id"] == "broken_kingdom"
        assert "name" in template
        assert "description" in template
        assert "opening_scene" in template
        assert "starting_location" in template

    def test_load_nonexistent_template(self):
        """Test loading a template that doesn't exist"""
        template = load_campaign_template("nonexistent_template")

        assert template is None

    def test_template_caching(self):
        """Test that templates are cached after first load"""
        # First load
        template1 = load_campaign_template("broken_kingdom")
        # Second load (should be cached)
        template2 = load_campaign_template("broken_kingdom")

        # Should be the same object (cached)
        assert template1 is template2


class TestOpeningNarration:
    """Test opening narration generation"""

    def test_opening_narration_with_street_urchin(self):
        """Test narration generation for street urchin origin"""
        narration = get_opening_narration("broken_kingdom", "street_urchin")

        assert narration is not None
        assert len(narration) > 100  # Should be substantial text
        assert isinstance(narration, str)

    def test_opening_narration_with_veteran(self):
        """Test narration generation for veteran origin"""
        narration = get_opening_narration("broken_kingdom", "veteran")

        assert narration is not None
        assert len(narration) > 100
        # Should contain veteran-specific context
        assert "war" in narration.lower() or "soldier" in narration.lower() or "veteran" in narration.lower()

    def test_opening_narration_with_acolyte(self):
        """Test narration generation for acolyte origin"""
        narration = get_opening_narration("broken_kingdom", "acolyte")

        assert narration is not None
        assert len(narration) > 100

    def test_opening_narration_with_unknown_origin(self):
        """Test narration generation with unknown origin uses fallback"""
        narration = get_opening_narration("broken_kingdom", "unknown_origin")

        assert narration is not None
        assert len(narration) > 100

    def test_opening_narration_invalid_template(self):
        """Test narration generation fails gracefully with invalid template"""
        with pytest.raises(ValueError):
            get_opening_narration("nonexistent_template", "street_urchin")


class TestSuggestedActions:
    """Test suggested actions retrieval"""

    def test_get_suggested_actions_broken_kingdom(self):
        """Test getting suggested actions for broken kingdom"""
        actions = get_suggested_actions("broken_kingdom")

        assert isinstance(actions, list)
        assert len(actions) >= 2  # Should have at least a couple options
        assert all(isinstance(action, str) for action in actions)

    def test_get_suggested_actions_nonexistent_template(self):
        """Test suggested actions for nonexistent template returns defaults"""
        actions = get_suggested_actions("nonexistent_template")

        assert isinstance(actions, list)
        assert len(actions) >= 2
        assert "Look around" in actions or "Wait and observe" in actions


class TestStartingLocation:
    """Test starting location retrieval"""

    def test_get_starting_location_broken_kingdom(self):
        """Test getting starting location for broken kingdom"""
        location = get_starting_location("broken_kingdom")

        assert isinstance(location, str)
        assert len(location) > 0
        assert location == "The Crossroads Inn"

    def test_get_starting_location_nonexistent_template(self):
        """Test starting location for nonexistent template returns default"""
        location = get_starting_location("nonexistent_template")

        assert location == "Unknown Location"


class TestTemplateInfo:
    """Test template info retrieval"""

    def test_get_template_info_broken_kingdom(self):
        """Test getting template info for broken kingdom"""
        info = get_template_info("broken_kingdom")

        assert isinstance(info, dict)
        assert "template_id" in info
        assert "name" in info
        assert "description" in info
        assert "starting_location" in info
        assert info["template_id"] == "broken_kingdom"

    def test_get_template_info_nonexistent_template(self):
        """Test getting info for nonexistent template returns error info"""
        info = get_template_info("nonexistent_template")

        assert isinstance(info, dict)
        assert info["template_id"] == "nonexistent_template"
        assert info["name"] == "Unknown Campaign"
        assert info["description"] == "Template not found"


class TestTemplateValidation:
    """Test template validation"""

    def test_validate_broken_kingdom_template(self):
        """Test that broken kingdom template is valid"""
        is_valid = validate_template("broken_kingdom")

        assert is_valid is True

    def test_validate_nonexistent_template(self):
        """Test that nonexistent template is invalid"""
        is_valid = validate_template("nonexistent_template")

        assert is_valid is False
