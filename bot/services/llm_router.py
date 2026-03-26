import json
import sys
from typing import Any

import httpx

from config import config
from services.lms_client import (
    BackendError,
    get_completion_rate,
    get_groups,
    get_items,
    get_learners,
    get_pass_rates,
    get_scores,
    get_timeline,
    get_top_learners,
    trigger_sync,
)


SYSTEM_PROMPT = """You are an LMS analytics assistant.
Use tools whenever the user asks about labs, learners, groups, scores, pass rates, timelines, rankings, or data refresh.
Do not guess backend data. Use tools first.
For greetings, answer briefly and explain capabilities.
For gibberish or unclear messages, reply with a helpful clarification.
If a question requires comparing labs, groups, or learners, you may call multiple tools and reason across results.
Always produce a concise final answer with concrete data when available.
"""


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List all labs and tasks in the LMS",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "List enrolled students and groups",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier like lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier like lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier like lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group results and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier like lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners, optionally for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Optional lab identifier"},
                    "limit": {"type": "integer", "description": "Maximum number of learners to return"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier like lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh LMS data from autochecker",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


TOOL_IMPLS = {
    "get_items": lambda **kwargs: get_items(),
    "get_learners": lambda **kwargs: get_learners(),
    "get_scores": lambda **kwargs: get_scores(kwargs["lab"]),
    "get_pass_rates": lambda **kwargs: get_pass_rates(kwargs["lab"]),
    "get_timeline": lambda **kwargs: get_timeline(kwargs["lab"]),
    "get_groups": lambda **kwargs: get_groups(kwargs["lab"]),
    "get_top_learners": lambda **kwargs: get_top_learners(kwargs.get("lab"), kwargs.get("limit", 5)),
    "get_completion_rate": lambda **kwargs: get_completion_rate(kwargs["lab"]),
    "trigger_sync": lambda **kwargs: trigger_sync(),
}


def _call_llm(messages: list[dict[str, Any]]) -> dict[str, Any]:
    response = httpx.post(
        f"{config.llm_api_base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {config.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.llm_api_model,
            "messages": messages,
            "tools": TOOL_SCHEMAS,
            "tool_choice": "auto",
        },
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()


def route(user_text: str) -> str:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    for _ in range(8):
        data = _call_llm(messages)
        message = data["choices"][0]["message"]

        tool_calls = message.get("tool_calls")
        if tool_calls:
            messages.append(message)

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                raw_args = tool_call["function"].get("arguments", "{}")
                args = json.loads(raw_args or "{}")

                print(f"[tool] LLM called: {tool_name}({json.dumps(args, ensure_ascii=False)})", file=sys.stderr)

                try:
                    result = TOOL_IMPLS[tool_name](**args)
                except BackendError as exc:
                    result = {"error": str(exc)}
                except Exception as exc:
                    result = {"error": f"Unhandled tool error: {exc}"}

                if isinstance(result, list):
                    debug_result = f"{len(result)} items"
                elif isinstance(result, dict):
                    debug_result = json.dumps(result, ensure_ascii=False)[:200]
                else:
                    debug_result = str(result)[:200]

                print(f"[tool] Result: {debug_result}", file=sys.stderr)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

            print("[summary] Feeding tool results back to LLM", file=sys.stderr)
            continue

        content = message.get("content")
        if content:
            return content.strip()

    return "I could not complete the request. Please try again."
