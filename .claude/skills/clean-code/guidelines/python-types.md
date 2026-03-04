# Python Type Hint Patterns

Project-grounded examples for type hints used in Vigile.

## Function Signature Type Hints

Every function must have type hints on all parameters and the return type:

```python
# Correct — fully typed
def get_season(month: int) -> str:
    ...

def build_html(brief_text: str) -> str:
    ...

def send_email(
    html_body: str,
    subject: str,
    sender: str,
    password: str,
    recipients: list[str],
) -> None:
    ...

def main() -> None:
    ...
```

## Built-in Generic Types (Python 3.9+)

Use built-in generics directly — no need for `typing` module equivalents:

```python
# Correct — Python 3.9+ built-ins
def send_email(recipients: list[str]) -> None: ...
def parse_emails(raw: str) -> list[str]: ...

# Avoid — legacy typing module
from typing import List
def send_email(recipients: List[str]) -> None: ...  # Unnecessary
```

## Union Types (Python 3.10+)

Use `X | Y` syntax instead of `Optional[X]` or `Union[X, Y]`:

```python
# Correct — Python 3.10+ union
def get_color(emoji: str) -> str | None:
    return SECTION_COLORS.get(emoji)

# Avoid — legacy Optional
from typing import Optional
def get_color(emoji: str) -> Optional[str]: ...  # Verbose
```

## os.getenv Return Type

`os.getenv()` returns `str | None`. Validate before use:

```python
# Pattern: validate all at once, then access via os.environ
required = ["ANTHROPIC_API_KEY", "GMAIL_ADDRESS"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print(f"Error: missing: {', '.join(missing)}")
    sys.exit(1)

# After validation, os.environ[key] returns str (not str | None)
api_key: str = os.environ["ANTHROPIC_API_KEY"]
```

## Constants with Type Hints

Module-level constants can use type hints for clarity:

```python
SECTION_COLORS: dict[str, str] = {
    "🔴": "#c0392b",
    "🟡": "#d68910",
}

MONTH_NAMES: list[str] = [
    "January", "February", ...
]
```

## When Not to Over-Type

Don't add redundant type hints that are obvious from context:

```python
# Redundant — type is obvious from the literal
x: int = 42           # Unnecessary
name: str = "Ablo"    # Unnecessary

# Useful — clarifies intent at function boundaries
def get_season(month: int) -> str:   # Needed — documents contract
```
