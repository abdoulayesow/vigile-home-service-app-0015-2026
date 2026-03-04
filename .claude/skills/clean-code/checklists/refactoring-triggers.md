# Refactoring Triggers

When to refactor and what to look for. If any of these conditions apply, consider refactoring before committing.

## Size Triggers

- [ ] **`vigile.py` > 200 lines** → Consider splitting into focused modules (e.g., `email_utils.py`, `prompt.py`)
- [ ] **Function > 30 lines** → Break into smaller functions with clear names
- [ ] **`main()` > 40 lines** → Extract sub-functions for logical phases

## Duplication Triggers

- [ ] **Same env var access pattern repeated** → Extract to a `get_required_env(name)` helper
- [ ] **Same HTML generation pattern** → Extract to a dedicated function
- [ ] **Same error print + exit pattern** → Consider a `fail(message)` helper

## Complexity Triggers

- [ ] **Function > 3 parameters** → Use a dataclass or typed dict
  ```python
  # Before
  def send_email(html_body, subject, sender, password, recipients): ...
  # After
  @dataclass
  class EmailConfig:
      sender: str
      password: str
      recipients: list[str]
  def send_email(html_body: str, subject: str, config: EmailConfig) -> None: ...
  ```
- [ ] **Nested conditionals > 2 levels** → Use early returns or helper functions
- [ ] **Long list comprehension > 1 line** → Extract to a named function with a clear name

## Magic Values

- [ ] **Magic string in HTML** → Extract to a constant (`SECTION_COLORS`, etc.)
- [ ] **Magic number (port, max_tokens)** → Name it: `SMTP_PORT = 587`, `MAX_TOKENS = 1500`
- [ ] **Hardcoded model name** → Extract: `CLAUDE_MODEL = "claude-sonnet-4-20250514"`

## Python Anti-Patterns

- [ ] **`except Exception:` without binding** → Always use `except Exception as e:` to log context
- [ ] **String concatenation in a loop** → Use list + `"".join()` instead
- [ ] **`os.getenv(key)` called multiple times for same key** → Fetch once, store in variable
- [ ] **Implicit `None` return where `str` expected** → Add guard clause or default value

## Import Smell

- [ ] **Unused import** → Remove it (ruff will flag as F401)
- [ ] **`import *`** → Always use explicit imports
- [ ] **Third-party import before stdlib** → Reorder: stdlib, blank line, third-party
