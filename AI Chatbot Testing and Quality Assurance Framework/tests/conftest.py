import pytest

from tests.support import ChatbotSettings, request_headers


@pytest.fixture(scope="session")
def settings() -> ChatbotSettings:
    return ChatbotSettings.from_environment()


@pytest.fixture
def api_url(settings: ChatbotSettings) -> str:
    if not settings.api_url:
        pytest.skip("Set CHATBOT_API_URL to run chatbot API integration tests")
    return settings.api_url


@pytest.fixture
def auth_headers(settings: ChatbotSettings) -> dict[str, str]:
    if not settings.api_key:
        pytest.skip("Set CHATBOT_API_KEY to run authenticated chatbot tests")
    return request_headers(settings.api_key)
