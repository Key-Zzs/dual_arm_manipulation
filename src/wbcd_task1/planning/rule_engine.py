"""Task rule helpers."""

from __future__ import annotations


class RuleEngine:
    def is_state_enabled(self, state_name: str, states_config: dict) -> bool:
        return bool(states_config.get(state_name, {}).get("enabled", True))
