# LMS Telegram Bot - Development Plan

## Overview

This document outlines the implementation plan for the LMS Telegram bot. The bot provides students with access to their lab assignments, scores, and course information through a conversational interface powered by an LLM.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Entry Point** (`bot.py`) - Handles Telegram connection and CLI test mode
2. **Handlers** (`handlers/`) - Command logic as pure functions (no Telegram dependency)
3. **Services** (`services/`) - External API clients (LMS backend, LLM)
4. **Configuration** (`config.py`) - Environment variable loading with validation

This architecture enables **testable handlers**: the same handler function works in test mode, unit tests, and production Telegram deployment.

## Task Breakdown

### Task 1: Scaffold (Current)

Create the project skeleton with testable handler architecture:
- Entry point with `--test` mode support
- Handler directory structure with placeholder commands
- Configuration loading from `.env.bot.secret`
- This development plan document

**Key pattern**: Handlers are functions that take input and return strings. They don't import Telegram libraries, making them trivial to test.

### Task 2: Backend Integration

Implement real API calls to the LMS backend:
- Create `services/api_client.py` with Bearer token authentication
- Implement `/health`, `/labs`, `/scores` handlers using the API client
- Handle API errors gracefully (timeouts, auth failures, missing data)
- Environment-based configuration for `LMS_API_BASE_URL` and `LMS_API_KEY`

**Key pattern**: API client encapsulates HTTP details. Handlers call the client and format responses.

### Task 3: LLM Intent Routing

Add natural language understanding using an LLM:
- Create `services/llm_client.py` for tool-calling with the LLM
- Define tools for each command (get_labs, get_scores, health_check)
- Write detailed tool descriptions so the LLM knows when to call each tool
- Implement intent router that queries the LLM for non-slash-command messages

**Key pattern**: Tool descriptions drive LLM behavior. Quality descriptions > prompt engineering.

### Task 4: Docker Deployment

Containerize the bot for production deployment:
- Create `Dockerfile` for the bot service
- Configure Docker networking (containers use service names, not localhost)
- Add bot service to `docker-compose.yml`
- Handle secrets via environment files (`.env.bot.secret` mounted at runtime)

**Key pattern**: Docker networking uses service names. The bot container connects to `backend:42002`, not `localhost:42002`.

## Testing Strategy

- **Test mode**: `uv run bot.py --test "/command"` runs handlers without Telegram
- **Unit tests**: Test handlers directly with mocked services
- **Integration tests**: Test full flow with test doubles for external services

## File Structure

```
bot/
├── bot.py              # Entry point with --test mode
├── config.py           # Environment configuration
├── pyproject.toml      # Dependencies
├── PLAN.md             # This file
├── handlers/
│   ├── __init__.py
│   ├── commands.py     # Slash command handlers
│   └── intent.py       # LLM-based intent router (Task 3)
└── services/
    ├── __init__.py
    ├── api_client.py   # LMS API client (Task 2)
    └── llm_client.py   # LLM client (Task 3)
```

## Success Criteria

- All handlers work in test mode before Telegram integration
- API calls use Bearer token auth from environment variables
- LLM correctly routes natural language queries to tools
- Docker deployment connects bot to backend via service names
