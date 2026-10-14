import pytest

from tests.support import (
    ChatbotSettings,
    answer_from_response,
    contains_refusal,
    expected_empty_status_codes,
    mentions_software_testing,
    request_headers,
)


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


def test_settings_read_environment(monkeypatch) -> None:
    monkeypatch.setenv("CHATBOT_API_URL", "https://example.test/chat")
    monkeypatch.setenv("CHATBOT_API_KEY", "configured-test-key")
    monkeypatch.setenv("CHATBOT_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("CHATBOT_RESPONSE_FIELD", "data.answer")

    settings = ChatbotSettings.from_environment()

    assert settings.api_url == "https://example.test/chat"
    assert settings.api_key == "configured-test-key"
    assert settings.timeout_seconds == 12.5
    assert settings.response_field == "data.answer"


def test_settings_reject_non_positive_timeout(monkeypatch) -> None:
    monkeypatch.setenv("CHATBOT_TIMEOUT_SECONDS", "0")

    with pytest.raises(ValueError, match="greater than zero"):
        ChatbotSettings.from_environment()


@pytest.mark.parametrize("timeout", ["nan", "inf"])
def test_settings_reject_non_finite_timeout(monkeypatch, timeout: str) -> None:
    monkeypatch.setenv("CHATBOT_TIMEOUT_SECONDS", timeout)

    with pytest.raises(ValueError, match="greater than zero"):
        ChatbotSettings.from_environment()


def test_request_headers_use_bearer_authentication() -> None:
    assert request_headers("test-key") == {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-key",
    }


def test_answer_from_response_reads_nested_field() -> None:
    response = FakeResponse({"data": {"answer": "  A useful answer.  "}})

    assert answer_from_response(response, "data.answer") == "A useful answer."


@pytest.mark.parametrize(
    ("data", "field_path", "message"),
    [
        ({"answer": 42}, "answer", "non-empty string"),
        ({"data": {}}, "data.answer", "missing the configured field"),
    ],
)
def test_answer_from_response_rejects_invalid_answer(
    data, field_path: str, message: str
) -> None:
    with pytest.raises(AssertionError, match=message):
        answer_from_response(FakeResponse(data), field_path)


def test_relevance_and_refusal_heuristics(monkeypatch) -> None:
    assert mentions_software_testing("Testing improves software quality.")
    assert not mentions_software_testing("The weather is sunny.")

    monkeypatch.setenv("CHATBOT_REFUSAL_TERMS", "I cannot do that,Not allowed")
    assert contains_refusal("I cannot do that.")
    assert not contains_refusal("Here are the requested details.")


def test_empty_input_status_codes_are_configurable(monkeypatch) -> None:
    monkeypatch.setenv("CHATBOT_EMPTY_INPUT_STATUS_CODES", "400, 422")
    assert expected_empty_status_codes() == {400, 422}

    for invalid_codes in ("200", "401,422"):
        monkeypatch.setenv("CHATBOT_EMPTY_INPUT_STATUS_CODES", invalid_codes)
        with pytest.raises(ValueError, match="client-input 4xx"):
            expected_empty_status_codes()
