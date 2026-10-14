from __future__ import annotations

import os
import re
from dataclasses import dataclass
from math import isfinite
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import requests


@dataclass(frozen=True)
class ChatbotSettings:
    api_url: str
    api_key: str
    response_field: str
    timeout_seconds: float

    @classmethod
    def from_environment(cls) -> "ChatbotSettings":
        timeout_value = os.getenv("CHATBOT_TIMEOUT_SECONDS", "30")
        try:
            timeout_seconds = float(timeout_value)
        except ValueError as exc:
            raise ValueError("CHATBOT_TIMEOUT_SECONDS must be a number") from exc
        if not isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("CHATBOT_TIMEOUT_SECONDS must be greater than zero")

        return cls(
            api_url=os.getenv("CHATBOT_API_URL", "").strip(),
            api_key=os.getenv("CHATBOT_API_KEY", "").strip(),
            response_field=os.getenv("CHATBOT_RESPONSE_FIELD", "response").strip(),
            timeout_seconds=timeout_seconds,
        )


def request_headers(api_key: str = "") -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def ask_chatbot(
    api_url: str,
    message: str,
    headers: dict[str, str],
    timeout_seconds: float,
) -> requests.Response:
    import requests

    return requests.post(
        api_url,
        headers=headers,
        json={"message": message},
        timeout=timeout_seconds,
    )


def answer_from_response(response: requests.Response, field_path: str) -> str:
    try:
        data: Any = response.json()
    except ValueError as exc:
        raise AssertionError("Chatbot response was not valid JSON") from exc

    for field in filter(None, field_path.split(".")):
        if not isinstance(data, dict) or field not in data:
            raise AssertionError(
                f"Chatbot response is missing the configured field {field_path!r}"
            )
        data = data[field]

    if not isinstance(data, str) or not data.strip():
        raise AssertionError(
            f"Chatbot response field {field_path!r} must be a non-empty string"
        )
    return data.strip()


def mentions_software_testing(answer: str) -> bool:
    return bool(
        re.search(r"\b(software|test\w*|quality|bug\w*|validation)\b", answer, re.I)
    )


def contains_refusal(answer: str) -> bool:
    configured_terms = os.getenv("CHATBOT_REFUSAL_TERMS", "")
    terms = (
        [term.strip() for term in configured_terms.split(",") if term.strip()]
        if configured_terms
        else [
            "can't help",
            "cannot help",
            "can't assist",
            "cannot assist",
            "won't provide",
            "unable to help",
            "not able to help",
        ]
    )
    normalized_answer = answer.casefold()
    return any(term.casefold() in normalized_answer for term in terms)


def expected_empty_status_codes() -> set[int]:
    raw_codes = os.getenv("CHATBOT_EMPTY_INPUT_STATUS_CODES", "400,422")
    try:
        codes = {int(code.strip()) for code in raw_codes.split(",") if code.strip()}
    except ValueError as exc:
        raise ValueError(
            "CHATBOT_EMPTY_INPUT_STATUS_CODES must be comma-separated HTTP status codes"
        ) from exc
    if not codes or any(
        code < 400 or code >= 500 or code in {401, 403} for code in codes
    ):
        raise ValueError(
            "CHATBOT_EMPTY_INPUT_STATUS_CODES must contain client-input 4xx "
            "statuses, excluding authentication errors"
        )
    return codes
