# Testing Patterns

Project-grounded examples for testing Vigile with pytest.

## AAA Pattern

Every test follows Arrange → Act → Assert:

```python
def test_get_season_returns_spring_for_march():
    # Arrange — nothing to set up for a pure function

    # Act — call the function under test
    result = get_season(3)

    # Assert — verify outcome
    assert result == "Spring"
```

## Testing Pure Functions (No Mocks Needed)

Pure functions like `get_season` and `build_html` can be tested directly:

```python
def test_get_season_spring():
    assert get_season(3) == "Spring"
    assert get_season(4) == "Spring"
    assert get_season(5) == "Spring"

def test_get_season_summer():
    assert get_season(6) == "Summer"
    assert get_season(9) == "Summer"

def test_get_season_fall():
    assert get_season(10) == "Fall"
    assert get_season(11) == "Fall"

def test_get_season_winter():
    assert get_season(12) == "Winter"
    assert get_season(1) == "Winter"
    assert get_season(2) == "Winter"
```

## Mocking External Calls

Use `unittest.mock.patch` to mock the Anthropic client and smtplib:

```python
from unittest.mock import MagicMock, patch

def test_main_calls_anthropic_api(monkeypatch):
    # Arrange
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("GMAIL_ADDRESS", "test@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "test-pass")
    monkeypatch.setenv("RECIPIENT_EMAILS", "recipient@gmail.com")

    mock_message = MagicMock()
    mock_message.content[0].text = "Hey Ablo! Here is your brief."

    with patch("anthropic.Anthropic") as mock_client_cls, \
         patch("smtplib.SMTP") as mock_smtp:
        mock_client_cls.return_value.messages.create.return_value = mock_message
        mock_smtp.return_value.__enter__.return_value = MagicMock()

        # Act
        from vigile import main
        # main() calls sys.exit(0) on success — catch SystemExit
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Assert
        assert exc_info.value.code == 0
        mock_client_cls.return_value.messages.create.assert_called_once()
```

## Testing Environment Variable Validation

```python
def test_main_exits_1_when_api_key_missing(monkeypatch):
    # Arrange — unset the API key
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("GMAIL_ADDRESS", "test@gmail.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "test-pass")
    monkeypatch.setenv("RECIPIENT_EMAILS", "test@gmail.com")

    # Act + Assert
    with pytest.raises(SystemExit) as exc_info:
        from vigile import main
        main()
    assert exc_info.value.code == 1
```

## Testing HTML Building

```python
def test_build_html_escapes_html_entities():
    from vigile import build_html
    result = build_html("5 > 3 & 2 < 4")
    assert "&gt;" in result
    assert "&lt;" in result
    assert "&amp;" in result

def test_build_html_styles_urgent_section():
    from vigile import build_html
    result = build_html("🔴 Urgent\nCheck your HVAC filter.")
    assert "#c0392b" in result  # Red color for urgent
    assert "font-weight: bold" in result
```

## Edge Cases to Cover

| Edge Case | What It Tests |
|---|---|
| Empty `RECIPIENT_EMAILS` | `sys.exit(1)` with clear message |
| Whitespace-only email address | Filtered out by `if e.strip()` |
| Claude returns empty content | `IndexError` or graceful exit |
| All four env vars missing | All names reported in one error |

## Test File Organization

```
vigile.py              # Source
vigile_test.py         # Tests (or tests/test_vigile.py)
```

## Running Tests

```bash
pip install pytest
python -m pytest vigile_test.py -v
```
