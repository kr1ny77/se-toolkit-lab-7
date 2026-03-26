"""Command handlers for test mode and Telegram mode."""

from services.lms_client import BackendError, get_items, get_pass_rates


def handle_start() -> str:
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    return """Available commands:
/start - Start the bot and see welcome message
/help - Show this help message
/health - Check backend connection status
/labs - List available labs
/scores <lab_id> - Get pass rates for a specific lab"""


def handle_health() -> str:
    try:
        items = get_items()
        return f"Backend is healthy. {len(items)} items available."
    except BackendError as exc:
        return str(exc)


def handle_labs() -> str:
    try:
        items = get_items()
    except BackendError as exc:
        return str(exc)

    labs = []
    for item in items:
        item_type = str(item.get("type", "")).lower()
        item_id = str(item.get("id", ""))
        title = str(item.get("title", item.get("name", item_id)))

        if item_type == "lab" or item_id.startswith("lab-"):
            labs.append((item_id, title))

    if not labs:
        return "No labs found in backend data."

    lines = ["Available labs:"]
    for lab_id, title in labs:
        lines.append(f"- {lab_id}: {title}")
    return "\n".join(lines)


def handle_scores(lab_id: str | None = None) -> str:
    if not lab_id:
        return "Usage: /scores <lab_id> (e.g., /scores lab-04)"

    try:
        rows = get_pass_rates(lab_id)
    except BackendError as exc:
        return str(exc)

    if not rows:
        return f"No pass-rate data found for {lab_id}."

    lines = [f"Pass rates for {lab_id}:"]
    for row in rows:
        task_name = (
            row.get("task")
            or row.get("task_name")
            or row.get("name")
            or "Unknown task"
        )

        rate = (
            row.get("pass_rate")
            or row.get("avg_pass_rate")
            or row.get("percentage")
            or 0
        )

        attempts = row.get("attempts") or row.get("count") or row.get("submissions")

        try:
            rate_value = float(rate)
        except (TypeError, ValueError):
            rate_value = 0.0

        if attempts is not None:
            lines.append(f"- {task_name}: {rate_value:.1f}% ({attempts} attempts)")
        else:
            lines.append(f"- {task_name}: {rate_value:.1f}%")

    return "\n".join(lines)
