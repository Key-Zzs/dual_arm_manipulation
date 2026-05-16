"""Recovery hooks for failed states."""

from __future__ import annotations


class RecoveryPolicy:
    def recover(self, state_name: str, context) -> None:
        if getattr(context, "dry_run", False):
            return
        execution = getattr(context, "execution", None)
        if execution is not None and state_name.startswith("align"):
            execution.go_home(getattr(context, "default_arm", "right"))
