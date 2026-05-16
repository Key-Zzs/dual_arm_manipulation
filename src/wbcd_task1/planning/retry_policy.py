"""Retry policy."""

from __future__ import annotations


class RetryPolicy:
    def __init__(self, default_max_retries: int = 1):
        self.default_max_retries = int(default_max_retries)

    def max_retries_for(self, state_name: str, state_config: dict | None = None) -> int:
        if state_config and "max_retries" in state_config:
            return int(state_config["max_retries"])
        return self.default_max_retries
