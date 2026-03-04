# Naming Conventions

Comprehensive naming rules with examples from the Vigile codebase.

## File Naming

| Pattern | Convention | Example |
|---|---|---|
| Main script | lowercase | `vigile.py` |
| Utilities (if extracted) | snake_case | `email_utils.py`, `prompt.py` |
| Tests | source name + `_test.py` | `vigile_test.py` |
| Config/workflows | kebab-case | `monthly_briefing.yml`, `ci.yml` |

## Function Naming

| Pattern | Convention | Examples |
|---|---|---|
| Data building | `build_` + noun | `build_html()` |
| Getters | `get_` + noun | `get_season()` |
| Actions | verb + noun | `send_email()`, `generate_brief()` |
| Entry point | `main` | `main()` |

## Variable & Constant Naming

| Pattern | Convention | Examples |
|---|---|---|
| Module-level constants | `UPPER_SNAKE_CASE` | `SYSTEM_PROMPT`, `SECTION_COLORS`, `MONTH_NAMES` |
| Local variables | `snake_case` | `brief_text`, `html_body`, `month_name` |
| Loop variables | descriptive | `emoji`, `color`, `line`, `stripped` |
| Error variables | `e` (in `except`) | `except Exception as e:` |
| Config strings | descriptive | `gmail_address`, `gmail_app_password` |

## Boolean Naming

Always prefix booleans with `is`, `has`, `should`, or `can`:

```python
is_missing = not os.getenv("ANTHROPIC_API_KEY")
has_recipients = len(recipients) > 0
```

## Constants with Purpose Comments

Add a comment when the value isn't self-explanatory:

```python
# 1st of month at 13:00 UTC = 8am CST
CRON_SCHEDULE = "0 13 1 * *"

# Gmail SMTP with STARTTLS
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Max tokens for the monthly brief
MAX_TOKENS = 1500
```

## Environment Variable Names

Match GitHub Secrets naming exactly — `UPPER_SNAKE_CASE`:

```python
# Access pattern — consistent naming
api_key = os.environ["ANTHROPIC_API_KEY"]
gmail_address = os.environ["GMAIL_ADDRESS"]
gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
recipient_emails_raw = os.environ["RECIPIENT_EMAILS"]
```

Local variable names (`api_key`, `gmail_address`) use `snake_case` per PEP 8.
