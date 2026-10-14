import time

from tests.support import answer_from_response, ask_chatbot, mentions_software_testing


def test_valid_question_returns_a_non_empty_answer(
    api_url: str, auth_headers: dict[str, str], settings
) -> None:
    response = ask_chatbot(
        api_url, "What is Python?", auth_headers, settings.timeout_seconds
    )

    assert 200 <= response.status_code < 300, response.text
    answer = answer_from_response(response, settings.response_field)
    assert answer


def test_software_testing_question_is_relevant(
    api_url: str, auth_headers: dict[str, str], settings
) -> None:
    response = ask_chatbot(
        api_url,
        "What is software testing?",
        auth_headers,
        settings.timeout_seconds,
    )

    assert 200 <= response.status_code < 300, response.text
    answer = answer_from_response(response, settings.response_field)
    assert mentions_software_testing(answer), (
        "Answer did not contain any expected software-testing concepts: "
        f"{answer!r}"
    )


def test_long_question_is_handled_without_server_error(
    api_url: str, auth_headers: dict[str, str], settings
) -> None:
    message = "Please explain how software testing helps find defects. " * 200
    response = ask_chatbot(api_url, message, auth_headers, settings.timeout_seconds)

    assert 200 <= response.status_code < 300, response.text
    answer_from_response(response, settings.response_field)


def test_response_completes_within_configured_timeout(
    api_url: str, auth_headers: dict[str, str], settings
) -> None:
    start_time = time.perf_counter()
    response = ask_chatbot(
        api_url,
        "What is software testing?",
        auth_headers,
        settings.timeout_seconds,
    )
    elapsed_seconds = time.perf_counter() - start_time

    assert 200 <= response.status_code < 300, response.text
    assert elapsed_seconds <= settings.timeout_seconds, (
        f"Response took {elapsed_seconds:.2f}s; "
        f"limit is {settings.timeout_seconds:.2f}s"
    )
    answer_from_response(response, settings.response_field)
