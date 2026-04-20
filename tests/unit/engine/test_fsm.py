"""
Unit tests for NodeFSM (cine_mate/engine/fsm.py)

Tests:
- State transitions (valid)
- Invalid transitions (error handling)
- Retry mechanism
- Terminal state handling
"""

import pytest
from cine_mate.engine.fsm import NodeFSM, NodeState, FSMError


class TestNodeState:
    """Tests for NodeState enum."""

    def test_all_states_exist(self):
        """Test all expected states exist."""
        expected_states = [
            "pending", "queued", "executing", "quality_check",
            "approval", "succeeded", "failed", "retrying",
            "skipped", "cancelled"
        ]
        for state in expected_states:
            assert hasattr(NodeState, state.upper()) or NodeState(state)

    def test_state_string_values(self):
        """Test state string values."""
        assert NodeState.PENDING.value == "pending"
        assert NodeState.EXECUTING.value == "executing"
        assert NodeState.SUCCEEDED.value == "succeeded"
        assert NodeState.FAILED.value == "failed"


class TestFSMCreation:
    """Tests for FSM initialization."""

    def test_fsm_creation(self, fsm):
        """Test basic FSM creation."""
        assert fsm.node_id == "test_node_001"
        assert fsm.state == NodeState.PENDING
        assert fsm.retry_count == 0
        assert fsm.max_retries == 2

    def test_fsm_custom_max_retries(self, fsm_with_retries):
        """Test FSM with custom max_retries."""
        assert fsm_with_retries.max_retries == 3

    def test_fsm_default_max_retries(self):
        """Test default max_retries is 2."""
        fsm = NodeFSM("test")
        assert fsm.max_retries == 2


class TestValidTransitions:
    """Tests for valid state transitions."""

    def test_pending_to_queued(self, fsm):
        """Test PENDING -> QUEUED transition."""
        fsm.transition("schedule")
        assert fsm.state == NodeState.QUEUED

    def test_pending_to_cancelled(self, fsm):
        """Test PENDING -> CANCELLED transition."""
        fsm.transition("cancel")
        assert fsm.state == NodeState.CANCELLED

    def test_queued_to_executing(self, fsm):
        """Test QUEUED -> EXECUTING transition."""
        fsm.transition("schedule")  # PENDING -> QUEUED
        fsm.transition("start")     # QUEUED -> EXECUTING
        assert fsm.state == NodeState.EXECUTING

    def test_queued_to_cancelled(self, fsm):
        """Test QUEUED -> CANCELLED transition."""
        fsm.transition("schedule")
        fsm.transition("cancel")
        assert fsm.state == NodeState.CANCELLED

    def test_executing_to_quality_check(self, fsm):
        """Test EXECUTING -> QUALITY_CHECK transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        assert fsm.state == NodeState.QUALITY_CHECK

    def test_executing_to_failed(self, fsm):
        """Test EXECUTING -> FAILED transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("error")
        assert fsm.state == NodeState.FAILED

    def test_executing_to_cancelled(self, fsm):
        """Test EXECUTING -> CANCELLED transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("cancel")
        assert fsm.state == NodeState.CANCELLED

    def test_quality_check_to_succeeded(self, fsm):
        """Test QUALITY_CHECK -> SUCCEEDED transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("pass")
        assert fsm.state == NodeState.SUCCEEDED

    def test_quality_check_to_retrying(self, fsm):
        """Test QUALITY_CHECK -> RETRYING transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("fail")
        assert fsm.state == NodeState.RETRYING
        assert fsm.retry_count == 1

    def test_quality_check_to_approval(self, fsm):
        """Test QUALITY_CHECK -> APPROVAL transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("review")
        assert fsm.state == NodeState.APPROVAL

    def test_approval_to_succeeded(self, fsm):
        """Test APPROVAL -> SUCCEEDED transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("review")
        fsm.transition("approve")
        assert fsm.state == NodeState.SUCCEEDED

    def test_approval_to_retrying(self, fsm):
        """Test APPROVAL -> RETRYING transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("review")
        fsm.transition("reject")
        assert fsm.state == NodeState.RETRYING
        assert fsm.retry_count == 1

    def test_retrying_to_executing(self, fsm):
        """Test RETRYING -> EXECUTING transition."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("fail")
        fsm.transition("retry")
        assert fsm.state == NodeState.EXECUTING


class TestInvalidTransitions:
    """Tests for invalid state transitions."""

    def test_invalid_event_from_pending(self, fsm):
        """Test invalid event from PENDING state."""
        with pytest.raises(FSMError) as exc_info:
            fsm.transition("start")  # Can't start from PENDING
        assert "Invalid event" in str(exc_info.value)

    def test_invalid_event_from_executing(self, fsm):
        """Test invalid event from EXECUTING state."""
        fsm.transition("schedule")
        fsm.transition("start")
        with pytest.raises(FSMError) as exc_info:
            fsm.transition("schedule")  # Can't schedule from EXECUTING
        assert "Invalid event" in str(exc_info.value)

    def test_invalid_event_from_succeeded(self, fsm):
        """Test invalid event from terminal state SUCCEEDED."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("pass")  # Now SUCCEEDED (terminal)
        with pytest.raises(FSMError) as exc_info:
            fsm.transition("schedule")
        assert "terminal state" in str(exc_info.value)

    def test_invalid_event_from_failed(self, fsm):
        """Test invalid event from terminal state FAILED."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("error")  # Now FAILED (terminal)
        with pytest.raises(FSMError) as exc_info:
            fsm.transition("retry")
        assert "terminal state" in str(exc_info.value)

    def test_invalid_event_from_cancelled(self, fsm):
        """Test invalid event from terminal state CANCELLED."""
        fsm.transition("cancel")  # Now CANCELLED (terminal)
        with pytest.raises(FSMError) as exc_info:
            fsm.transition("schedule")
        assert "terminal state" in str(exc_info.value)


class TestRetryMechanism:
    """Tests for retry mechanism."""

    def test_first_retry_increments_count(self, fsm):
        """Test first retry increments retry_count."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("fail")
        assert fsm.retry_count == 1
        assert fsm.state == NodeState.RETRYING

    def test_retry_loop(self, fsm):
        """Test complete retry loop."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("fail")      # retry_count = 1
        fsm.transition("retry")     # -> EXECUTING
        fsm.transition("complete")  # -> QUALITY_CHECK
        fsm.transition("fail")      # retry_count = 2, max reached
        # Should auto-transition to FAILED
        assert fsm.state == NodeState.FAILED
        assert fsm.retry_count == 2

    def test_max_retries_auto_fail(self, fsm):
        """Test auto-fail when max_retries reached."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("fail")      # retry_count = 1
        fsm.transition("retry")
        fsm.transition("complete")
        fsm.transition("fail")      # retry_count = 2 (max for default)
        # Should auto fail
        assert fsm.state == NodeState.FAILED

    def test_custom_max_retries(self, fsm_with_retries):
        """Test FSM with custom max_retries allows more retries."""
        fsm_with_retries.transition("schedule")
        fsm_with_retries.transition("start")
        fsm_with_retries.transition("complete")
        fsm_with_retries.transition("fail")      # retry 1
        fsm_with_retries.transition("retry")
        fsm_with_retries.transition("complete")
        fsm_with_retries.transition("fail")      # retry 2
        fsm_with_retries.transition("retry")     # Should still work (max=3)
        assert fsm_with_retries.state == NodeState.EXECUTING

        fsm_with_retries.transition("complete")
        fsm_with_retries.transition("fail")      # retry 3, max reached
        assert fsm_with_retries.state == NodeState.FAILED

    def test_explicit_give_up_from_retrying(self, fsm):
        """Test explicit give_up from RETRYING state."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("fail")  # -> RETRYING
        fsm.transition("give_up")  # -> FAILED
        assert fsm.state == NodeState.FAILED


class TestTerminalStates:
    """Tests for terminal states."""

    def test_succeeded_is_terminal(self, fsm):
        """Test SUCCEEDED is terminal state."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("pass")
        # Any further transition should fail
        with pytest.raises(FSMError):
            fsm.transition("schedule")

    def test_failed_is_terminal(self, fsm):
        """Test FAILED is terminal state."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("error")
        with pytest.raises(FSMError):
            fsm.transition("retry")

    def test_cancelled_is_terminal(self, fsm):
        """Test CANCELLED is terminal state."""
        fsm.transition("cancel")
        with pytest.raises(FSMError):
            fsm.transition("schedule")

    def test_skipped_is_terminal(self):
        """Test SKIPPED is terminal state (via Orchestrator)."""
        fsm = NodeFSM("test")
        fsm.state = NodeState.SKIPPED
        with pytest.raises(FSMError):
            fsm.transition("schedule")


class TestFullExecutionPath:
    """Tests for complete execution paths."""

    def test_happy_path(self, fsm):
        """Test successful execution path."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("pass")
        assert fsm.state == NodeState.SUCCEEDED
        assert fsm.retry_count == 0

    def test_manual_review_path(self, fsm):
        """Test path with manual review."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("review")    # -> APPROVAL
        fsm.transition("approve")   # -> SUCCEEDED
        assert fsm.state == NodeState.SUCCEEDED

    def test_rejection_path(self, fsm):
        """Test path with rejection."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("review")
        fsm.transition("reject")    # -> RETRYING
        fsm.transition("retry")
        fsm.transition("complete")
        fsm.transition("pass")      # -> SUCCEEDED
        assert fsm.state == NodeState.SUCCEEDED
        assert fsm.retry_count == 1

    def test_error_recovery_path(self, fsm):
        """Test error recovery path."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("error")     # -> FAILED
        assert fsm.state == NodeState.FAILED
        # Cannot recover from FAILED (terminal)

    def test_cancel_at_different_stages(self, fsm):
        """Test cancellation at different stages."""
        # Cancel from PENDING
        fsm1 = NodeFSM("node_1")
        fsm1.transition("cancel")
        assert fsm1.state == NodeState.CANCELLED

        # Cancel from QUEUED
        fsm2 = NodeFSM("node_2")
        fsm2.transition("schedule")
        fsm2.transition("cancel")
        assert fsm2.state == NodeState.CANCELLED

        # Cancel from EXECUTING
        fsm3 = NodeFSM("node_3")
        fsm3.transition("schedule")
        fsm3.transition("start")
        fsm3.transition("cancel")
        assert fsm3.state == NodeState.CANCELLED


class TestFSMStateTracking:
    """Tests for state tracking features."""

    def test_state_transitions_are_recorded(self, fsm):
        """Test state transitions update state field."""
        states_visited = []
        fsm.transition("schedule")
        states_visited.append(fsm.state)
        fsm.transition("start")
        states_visited.append(fsm.state)
        fsm.transition("complete")
        states_visited.append(fsm.state)

        assert NodeState.QUEUED in states_visited
        assert NodeState.EXECUTING in states_visited
        assert NodeState.QUALITY_CHECK in states_visited

    def test_retry_count_preserved_across_retries(self, fsm):
        """Test retry_count is preserved across retry loop."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")
        fsm.transition("fail")      # retry_count = 1
        fsm.transition("retry")
        fsm.transition("complete")
        fsm.transition("fail")      # retry_count = 2
        assert fsm.retry_count == 2


@pytest.mark.unit
class TestFSMEdgeCases:
    """Edge case tests for FSM."""

    def test_multiple_quality_check_failures(self, fsm):
        """Test multiple quality check failures."""
        fsm.transition("schedule")
        fsm.transition("start")
        fsm.transition("complete")

        # First fail -> retry
        fsm.transition("fail")
        fsm.transition("retry")
        fsm.transition("complete")

        # Second fail -> retry (retry_count = 2)
        fsm.transition("fail")
        # Auto-fails because max_retries = 2
        assert fsm.state == NodeState.FAILED

    def test_transition_returns_new_state(self, fsm):
        """Test transition returns new state."""
        new_state = fsm.transition("schedule")
        assert new_state == NodeState.QUEUED
        assert new_state == fsm.state

    def test_fsm_error_message_contains_node_id(self, fsm):
        """Test FSMError contains node_id in message."""
        with pytest.raises(FSMError) as exc_info:
            fsm.transition("invalid_event")
        assert "test_node_001" in str(exc_info.value)