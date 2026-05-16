"""Project-specific exceptions."""


class WBCDTaskError(Exception):
    """Base exception for task-level failures."""


class ConfigError(WBCDTaskError):
    """Raised when a task configuration is invalid."""


class ExecutionError(WBCDTaskError):
    """Raised when the execution layer rejects or fails a command."""


class PerceptionError(WBCDTaskError):
    """Raised when perception cannot provide a required observation."""


class PlanningError(WBCDTaskError):
    """Raised when planning cannot produce a valid next action."""
