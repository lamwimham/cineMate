"""
Node Execution State Machine.
Controls the lifecycle of a single DAG node execution.
"""

from enum import Enum
from typing import Optional

class NodeState(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING = "executing"
    QUALITY_CHECK = "quality_check"
    APPROVAL = "approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class FSMError(Exception):
    pass

class NodeFSM:
    """
    State Machine for a single pipeline node.
    Transitions:
      PENDING -> QUEUED / CANCELLED
      QUEUED -> EXECUTING / CANCELLED
      EXECUTING -> QUALITY_CHECK / FAILED / CANCELLED
      QUALITY_CHECK -> SUCCEEDED / RETRYING / APPROVAL
      APPROVAL -> SUCCEEDED / RETRYING
      RETRYING -> EXECUTING / FAILED
      SKIPPED -> (Terminal)
      SUCCEEDED -> (Terminal)
      CANCELLED -> (Terminal)
      FAILED -> (Terminal)
    """
    
    def __init__(self, node_id: str, max_retries: int = 2):
        self.node_id = node_id
        self.state = NodeState.PENDING
        self.max_retries = max_retries
        self.retry_count = 0

    def transition(self, event: str) -> NodeState:
        """Process an event and transition state."""
        current = self.state
        
        # Define allowed transitions
        allowed = {
            NodeState.PENDING: {
                "schedule": NodeState.QUEUED,
                "cancel": NodeState.CANCELLED,
            },
            NodeState.QUEUED: {
                "start": NodeState.EXECUTING,
                "cancel": NodeState.CANCELLED,
            },
            NodeState.EXECUTING: {
                "complete": NodeState.QUALITY_CHECK,
                "error": NodeState.FAILED,
                "cancel": NodeState.CANCELLED,
            },
            NodeState.QUALITY_CHECK: {
                "pass": NodeState.SUCCEEDED,
                "fail": NodeState.RETRYING,
                "review": NodeState.APPROVAL,
            },
            NodeState.APPROVAL: {
                "approve": NodeState.SUCCEEDED,
                "reject": NodeState.RETRYING,
            },
            NodeState.RETRYING: {
                "retry": NodeState.EXECUTING,
                "give_up": NodeState.FAILED,
            }
        }
        
        # Terminal states (no outgoing transitions)
        # SUCCEEDED, FAILED, CANCELLED, SKIPPED
        
        if current in (NodeState.SUCCEEDED, NodeState.FAILED, NodeState.CANCELLED, NodeState.SKIPPED):
            raise FSMError(f"Node {self.node_id} is in terminal state {current}. Cannot process event '{event}'.")
        
        if current not in allowed:
            raise FSMError(f"Node {self.node_id} is in invalid state {current}.")
            
        if event not in allowed[current]:
            valid_events = list(allowed[current].keys())
            raise FSMError(f"Invalid event '{event}' for node {self.node_id} in state {current}. Allowed: {valid_events}")
            
        new_state = allowed[current][event]
        self.state = new_state
        
        if new_state == NodeState.RETRYING:
            self.retry_count += 1
            if self.retry_count >= self.max_retries:
                self.transition("give_up") # Auto fail if max retries reached
                
        return self.state
