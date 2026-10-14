# AI Chatbot Testing and Quality Assurance Framework

A configurable `pytest` suite for checking a chatbot HTTP API's basic response
structure, input handling, authentication, relevance, safety, and response time.
AI output varies: the relevance and safety checks use configurable heuristics,
not exact answer matching or a guarantee of safety. Review those results against
your API's documented behavior.

## Requirements

- Python 3.9 or later
- A chatbot API endpoint and, for authenticated tests, an API key

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Configure the API

Set configuration in your shell, CI secret store, or another secure environment
configuration method. Do not commit API keys.

```powershell
$env:CHATBOT_API_URL = "https://your-chatbot.example/api/chat"
$env:CHATBOT_API_KEY = "your-secret-key"
```

The starter integration assumes a `POST` request with
`{"message": "..."}`, a bearer token in the `Authorization` header, and a JSON
answer field named `response`. Override the answer field when needed:

```powershell
$env:CHATBOT_RESPONSE_FIELD = "data.answer"
```

For a different request body or authentication scheme, adapt
`ask_chatbot` / `request_headers` in [tests/support.py](tests/support.py) to the
API's documentation. The malformed-request test intentionally sends invalid
JSON and the authentication test expects `401` or `403`; update those
expectations if your API documents different behavior.

### Settings

| Variable | Default | Purpose |
| --- | --- | --- |
| `CHATBOT_API_URL` | unset | API endpoint. Without it, endpoint tests are skipped. |
| `CHATBOT_API_KEY` | unset | Bearer token. Authenticated tests are skipped without it; auth rejection tests still run when the URL is set. |
| `CHATBOT_RESPONSE_FIELD` | `response` | Dot-separated JSON path to a non-empty answer string. |
| `CHATBOT_TIMEOUT_SECONDS` | `30` | Per-request timeout and performance-test limit. |
| `CHATBOT_EMPTY_INPUT_STATUS_CODES` | `400,422` | Documented client-error statuses accepted for an empty message. |
| `CHATBOT_INVALID_API_KEY` | `invalid-test-key` | Deliberately invalid token used by the authentication test. |
| `CHATBOT_REFUSAL_TERMS` | Built-in phrase list | Comma-separated refusal phrases accepted by the safety heuristic. |

The empty-input check also accepts a successful response when its answer looks
like a validation prompt. Adjust the accepted status codes and prompt indicators
in [tests/test_invalid_input.py](tests/test_invalid_input.py) to match your API's
documented behavior.

## Run the tests

Run the suite with verbose output:

```powershell
python -m pytest -v -s
```

Generate a self-contained HTML report:

```powershell
python -m pytest -v --html=reports/report.html --self-contained-html
```

API tests are skipped when the endpoint or required credentials are not
configured. Pytest's summary shows passed, failed, and skipped cases.

## What is checked

- **Valid question:** a successful response with a non-empty answer.
- **Empty input:** a configured client-error status or an apparent validation
  prompt.
- **Long input:** the API completes with a successful response and answer.
- **Malformed request:** the API rejects invalid JSON with a client error.
- **Authentication:** requests without a key and with an invalid key are
  rejected.
- **Relevance:** a response to “What is software testing?” contains at least
  one related keyword. This is a lightweight smoke check; it cannot establish
  semantic relevance.
- **Safety:** a refusal response includes a configured refusal phrase. Review
  outputs manually; phrase matching cannot determine whether a response is
  actually safe.
- **Performance:** a normal response completes within the configured timeout.
