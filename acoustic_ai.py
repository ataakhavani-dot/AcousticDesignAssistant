"""Client and validation helpers for the public Acoustic Atlas AI API."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi


ACOUSTIC_AI_API_URL = "https://echo-muse-haven.lovable.app/api/public/acoustic-ai"
MINIMUM_WORD_COUNT = 4
MAXIMUM_MESSAGES = 40
MAXIMUM_CHARACTERS = 8_000
REQUEST_TIMEOUT_SECONDS = 60
ALLOWED_ROLES = {"user", "assistant", "system"}

DEFAULT_SUGGESTED_QUESTIONS = (
    "How do I calculate RT60 for a control room?",
    "What is the difference between absorption and diffusion?",
    "How thick should a bass trap be to treat 100 Hz?",
    "What is the best room shape for a home studio?",
    "How do STC and IIC ratings differ?",
    "How can I reduce flutter echo in a rectangular room?",
    "What are early reflections and why do they matter?",
    "How do I position studio monitors in a small room?",
    "What is a QRD diffuser and how does it work?",
    "How does speaker boundary interference affect low end?",
)


class AcousticAIError(RuntimeError):
    """Raised when Acoustic Atlas cannot provide a usable response."""


@dataclass(frozen=True)
class AcousticAIResponse:
    """The response fields used by the application."""

    reply: str
    suggested_questions: tuple[str, ...]
    model: str | None
    usage: Mapping[str, Any] | None


def validate_question(question: str) -> str | None:
    """Return a user-facing validation error without sending an API request."""
    normalized_question = question.strip()
    if not normalized_question:
        return "Enter an acoustics question before sending it."

    if len(normalized_question.split()) < MINIMUM_WORD_COUNT:
        return "Please use at least four words so Acoustic Atlas can give a useful answer."

    if len(normalized_question) > MAXIMUM_CHARACTERS:
        return "Keep the question under 8,000 characters before sending it."

    return None


def build_conversation(
    history: Sequence[Mapping[str, str]], question: str
) -> list[dict[str, str]]:
    """Create a valid, most-recent conversation window for the stateless API."""
    messages: list[dict[str, str]] = []
    for message in [*history, {"role": "user", "content": question}]:
        role = message.get("role")
        content = message.get("content")
        if role not in ALLOWED_ROLES or not isinstance(content, str) or not content.strip():
            continue
        messages.append({"role": role, "content": content.strip()})

    while messages and (
        len(messages) > MAXIMUM_MESSAGES
        or sum(len(message["content"]) for message in messages) > MAXIMUM_CHARACTERS
    ):
        messages.pop(0)

    while messages and messages[0]["role"] == "assistant":
        messages.pop(0)

    return messages


def ask_acoustic_ai(
    messages: Sequence[Mapping[str, str]],
    *,
    url: str = ACOUSTIC_AI_API_URL,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
) -> AcousticAIResponse:
    """Send a complete conversation to Acoustic Atlas and return its reply."""
    request_body = json.dumps({"messages": messages}).encode("utf-8")
    request = Request(
        url,
        data=request_body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AcousticDesignAssistant/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=timeout,
            context=ssl.create_default_context(cafile=certifi.where()),
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise AcousticAIError(_error_for_status(error.code)) from error
    except (URLError, TimeoutError) as error:
        raise AcousticAIError("Acoustic Atlas could not be reached. Check your connection and try again.") from error
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AcousticAIError("Acoustic Atlas returned an unreadable response. Please try again.") from error

    reply = payload.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise AcousticAIError("Acoustic Atlas returned an incomplete response. Please try again.")

    suggested_questions = _suggestions_from(payload)
    usage = payload.get("usage")
    return AcousticAIResponse(
        reply=reply.strip(),
        suggested_questions=suggested_questions,
        model=payload.get("model") if isinstance(payload.get("model"), str) else None,
        usage=usage if isinstance(usage, Mapping) else None,
    )


def _suggestions_from(payload: Mapping[str, Any]) -> tuple[str, ...]:
    suggestions = payload.get("suggestedQuestions")
    if isinstance(suggestions, list):
        valid_suggestions = tuple(
            suggestion.strip()
            for suggestion in suggestions
            if isinstance(suggestion, str) and suggestion.strip()
        )
        if valid_suggestions:
            return valid_suggestions
    return DEFAULT_SUGGESTED_QUESTIONS


def _error_for_status(status_code: int) -> str:
    messages = {
        400: "That request is not valid. Start a new question and try again.",
        402: "Acoustic Atlas has temporarily exhausted its shared AI credit.",
        429: "Acoustic Atlas is busy. Wait a moment, then try again.",
        500: "Acoustic Atlas is not configured right now. Please try again later.",
        502: "Acoustic Atlas could not reach its AI model. Please try again.",
    }
    return messages.get(status_code, "Acoustic Atlas could not complete that request. Please try again.")