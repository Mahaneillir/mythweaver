"""
Tests for Storyfire Economics System
Verifies configuration and exception handling for Storyfire system

NOTE: Full Storyfire service implementation (Week 4+) will require additional tests for:
- Storyfire balance tracking
- Daily Storyfire reset logic
- Storyfire deduction on actions
- Premium vs Free tier differentiation
"""
import pytest
from app.core.config import settings
from app.exceptions import StoryfireExhausted


class TestStoryfireConfiguration:
    """Test Storyfire economic configuration"""

    def test_storyfire_free_daily_is_40(self):
        """Test that free users get 40 Storyfire daily"""
        assert settings.STORYFIRE_FREE_DAILY == 40

    def test_storyfire_cost_per_action_is_2(self):
        """Test that each action costs 2 Storyfire"""
        assert settings.STORYFIRE_COST_PER_ACTION == 2

    def test_free_users_get_20_actions_per_day(self):
        """Test that 40 Storyfire = 20 actions for free users"""
        daily_storyfire = settings.STORYFIRE_FREE_DAILY
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        max_daily_actions = daily_storyfire // cost_per_action

        assert max_daily_actions == 20

    def test_storyfire_values_are_positive(self):
        """Test that Storyfire values are positive integers"""
        assert settings.STORYFIRE_FREE_DAILY > 0
        assert settings.STORYFIRE_COST_PER_ACTION > 0


class TestStoryfireExhaustedException:
    """Test Storyfire exhausted exception"""

    def test_storyfire_exhausted_exception_creation(self):
        """Test creating a StoryfireExhausted exception"""
        exception = StoryfireExhausted()

        assert exception.status_code == 402  # Payment Required
        assert "Storyfire" in exception.detail
        assert "Premium" in exception.detail
        assert exception.error_code == "STORYFIRE_EXHAUSTED"

    def test_storyfire_exhausted_custom_message(self):
        """Test StoryfireExhausted with custom message"""
        custom_message = "You need 5 more Storyfire to perform this action"
        exception = StoryfireExhausted(detail=custom_message)

        assert exception.detail == custom_message
        assert exception.status_code == 402

    def test_storyfire_exhausted_can_be_raised(self):
        """Test that StoryfireExhausted can be raised and caught"""
        with pytest.raises(StoryfireExhausted) as exc_info:
            raise StoryfireExhausted()

        assert exc_info.value.status_code == 402
        assert exc_info.value.error_code == "STORYFIRE_EXHAUSTED"


class TestStoryfireBusinessLogic:
    """Test Storyfire business logic calculations"""

    def test_calculate_required_storyfire_for_actions(self):
        """Test calculating Storyfire needed for N actions"""
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        # 1 action = 2 Storyfire
        assert 1 * cost_per_action == 2

        # 5 actions = 10 Storyfire
        assert 5 * cost_per_action == 10

        # 20 actions = 40 Storyfire (full daily allowance)
        assert 20 * cost_per_action == 40

    def test_calculate_max_actions_from_storyfire(self):
        """Test calculating how many actions can be performed with given Storyfire"""
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        # 10 Storyfire = 5 actions
        assert 10 // cost_per_action == 5

        # 40 Storyfire = 20 actions
        assert 40 // cost_per_action == 20

        # 50 Storyfire = 25 actions
        assert 50 // cost_per_action == 25

    def test_storyfire_remainder_calculation(self):
        """Test calculating leftover Storyfire after actions"""
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        # Starting with 40, after 1 action should have 38
        remaining = settings.STORYFIRE_FREE_DAILY - (1 * cost_per_action)
        assert remaining == 38

        # After 10 actions should have 20
        remaining = settings.STORYFIRE_FREE_DAILY - (10 * cost_per_action)
        assert remaining == 20

        # After 20 actions should have 0
        remaining = settings.STORYFIRE_FREE_DAILY - (20 * cost_per_action)
        assert remaining == 0

    def test_storyfire_insufficient_check(self):
        """Test checking if user has sufficient Storyfire"""
        current_storyfire = 5
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        # 5 Storyfire is enough for 2 actions (costs 4)
        can_perform_2_actions = current_storyfire >= (2 * cost_per_action)
        assert can_perform_2_actions is True

        # 5 Storyfire is NOT enough for 3 actions (costs 6)
        can_perform_3_actions = current_storyfire >= (3 * cost_per_action)
        assert can_perform_3_actions is False


class TestStoryfireEdgeCases:
    """Test edge cases for Storyfire system"""

    def test_zero_storyfire_cannot_perform_actions(self):
        """Test that 0 Storyfire cannot perform any actions"""
        current_storyfire = 0
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        can_perform_action = current_storyfire >= cost_per_action
        assert can_perform_action is False

    def test_one_storyfire_cannot_perform_action(self):
        """Test that 1 Storyfire cannot perform an action (costs 2)"""
        current_storyfire = 1
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        can_perform_action = current_storyfire >= cost_per_action
        assert can_perform_action is False

    def test_exactly_enough_storyfire(self):
        """Test having exactly enough Storyfire for an action"""
        current_storyfire = 2
        cost_per_action = settings.STORYFIRE_COST_PER_ACTION

        can_perform_action = current_storyfire >= cost_per_action
        assert can_perform_action is True

        remaining = current_storyfire - cost_per_action
        assert remaining == 0


# NOTE: Additional tests needed when Storyfire service is implemented (Week 4+):
#
# class TestStoryfireService:
#     def test_deduct_storyfire_from_user(self):
#         """Test deducting Storyfire from user balance"""
#         pass
#
#     def test_reset_daily_storyfire_for_free_users(self):
#         """Test daily Storyfire reset at midnight"""
#         pass
#
#     def test_premium_users_have_unlimited_storyfire(self):
#         """Test that premium users don't have Storyfire limits"""
#         pass
#
#     def test_storyfire_exhausted_raises_exception(self):
#         """Test that performing action without sufficient Storyfire raises exception"""
#         pass
#
#     def test_track_storyfire_usage_history(self):
#         """Test tracking Storyfire usage for analytics"""
#         pass
