"""Small retrying state machine for task orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from wbcd_task1.core.result import StateResult, TaskResult, TaskStatus
from wbcd_task1.planning.recovery_policy import RecoveryPolicy
from wbcd_task1.planning.retry_policy import RetryPolicy
from wbcd_task1.planning.rule_engine import RuleEngine

StateHandler = Callable[[object], StateResult]


@dataclass(frozen=True)
class StateSpec:
    name: str
    handler: StateHandler


class StateMachine:
    def __init__(
        self,
        states: list[StateSpec],
        *,
        retry_policy: RetryPolicy | None = None,
        recovery_policy: RecoveryPolicy | None = None,
        rule_engine: RuleEngine | None = None,
    ):
        self.states = states
        self.retry_policy = retry_policy or RetryPolicy()
        self.recovery_policy = recovery_policy or RecoveryPolicy()
        self.rule_engine = rule_engine or RuleEngine()

    def run(self, context, result: TaskResult) -> TaskResult:
        states_config = context.config.get("states", {})
        for spec in self.states:
            if not self.rule_engine.is_state_enabled(spec.name, states_config):
                result.add_state(StateResult(spec.name, TaskStatus.SKIPPED, "disabled", attempts=0))
                continue

            max_retries = self.retry_policy.max_retries_for(spec.name, states_config.get(spec.name, {}))
            last_state_result: StateResult | None = None
            for attempt in range(1, max_retries + 1):
                try:
                    state_result = spec.handler(context)
                    state_result.attempts = attempt
                except Exception as exc:
                    state_result = StateResult(
                        spec.name,
                        TaskStatus.FAILED,
                        message=str(exc),
                        attempts=attempt,
                    )
                last_state_result = state_result
                if state_result.ok:
                    result.add_state(state_result)
                    break
                self.recovery_policy.recover(spec.name, context)
            else:
                failed = last_state_result or StateResult(spec.name, TaskStatus.FAILED, "unknown failure")
                result.add_state(failed)
                result.status = TaskStatus.FAILED
                result.message = f"State failed: {spec.name}"
                return result

        result.status = TaskStatus.SUCCESS
        result.message = "Task completed"
        return result
