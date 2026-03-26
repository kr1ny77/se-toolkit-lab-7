"""Command handlers for the Telegram bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram — same function works from --test mode,
unit tests, or the Telegram bot. This is *separation of concerns*.
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
