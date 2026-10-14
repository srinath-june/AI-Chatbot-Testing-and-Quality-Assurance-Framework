import os

from tests.support import (
    answer_from_response,
    ask_chatbot,
    expected_empty_status_codes,
    request_headers,
)


def test_empty_input_is_rejected_or_gets_a_validation_prompt(
    api_url: str, auth_headers: dict[str, str], settings
) -> None:
    response = ask_chatbot(api_url, "", auth_headers, settings.timeout_seconds)
    expected_codes = expected_empty_status_codes()

    if response.status_code in expected_codes:
        return

    assert 200 <= response.status_code < 300, (
        f"Expected one of {sorted(expected_codes)} or a validation prompt; "
        f"received {response.status_code}: {response.text}"
    )
    answer = answer_from_response(response, settings.response_field).casefold()
    prompt_indicators = ("empty", "required", "provide", "enter", "question", "help")
    assert any(indicator in answer for indicator in prompt_indicators), (
        f"Successful empty-input response was not an apparent validation prompt: "
        f"{answer!r}"
    )


def test_malformed_json_request_returns_a_client_error(
    api_url: str, auth_headers: dict[str, str], settings
) -> None:
    import requests

    response = requests.post(
        api_url,
        headers=auth_headers,
        data='{"message": ',
        timeout=settings.timeout_seconds,
    )

    assert 400 <= response.status_code < 500 and response.status_code not in (401, 403), (
        f"Expected a 4xx response to malformed JSON; got "
        f"{response.status_code}: {response.text}"
    )


def test_missing_and_invalid_api_keys_are_rejected(
    api_url: str, settings
) -> None:
    for headers in (
        request_headers(),
        request_headers(os.getenv("CHATBOT_INVALID_API_KEY", "invalid-test-key")),
    ):
        response = ask_chatbot(
            api_url,
            "What is Python?",
            headers,
            settings.timeout_seconds,
        )
        assert response.status_code in (401, 403), (
            "Expected an authentication rejection (401 or 403), "
            f"got {response.status_code}: {response.text}"
        )
