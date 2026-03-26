"""Placeholder command handlers.

Each handler is a function that returns a string response.
In test mode, this gets printed to stdout.
In production mode, Telegram sends it as a message.
"""


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start - Start the bot and see welcome message
/help - Show this help message
/health - Check backend connection status
/labs - List available labs
/scores <lab_id> - Get scores for a specific lab"""


def handle_health() -> str:
    """Handle /health command."""
    # TODO: Task 2 - actually check backend health
    return "Health check: Backend status unknown (not yet implemented)"


def handle_labs() -> str:
    """Handle /labs command."""
    # TODO: Task 2 - fetch labs from backend
    return "Available labs: (not yet implemented)"


def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command.
    
    Args:
        lab_id: Optional lab identifier to get scores for.
    """
    # TODO: Task 2 - fetch scores from backend
    if lab_id:
        return f"Scores for {lab_id}: (not yet implemented)"
    return "Usage: /scores <lab_id> (e.g., /scores lab-04)"
