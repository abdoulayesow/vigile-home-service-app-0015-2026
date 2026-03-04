# Pre-Commit Code Review Checklist

Run through this checklist before committing changes.

## Security

- [ ] No hardcoded secrets, API keys, or passwords in source code
- [ ] All credentials read from `os.getenv()` or `os.environ`
- [ ] Error messages never print credential values
- [ ] SMTP uses STARTTLS (`smtp.starttls()`) before `smtp.login()`
- [ ] HTML content is escaped with `html.escape()` before embedding in email

## Environment Variables

- [ ] All four required env vars validated at startup before any external call
- [ ] Missing vars reported by name in a single error message
- [ ] `sys.exit(1)` called immediately if any required var is missing

## Error Handling

- [ ] Anthropic API call wrapped in `try/except`
- [ ] SMTP/email send wrapped in `try/except`
- [ ] Each `except` block prints a clear error message with context
- [ ] Each `except` block calls `sys.exit(1)`
- [ ] `sys.exit(0)` called on success (not implicit exit)

## Python Style

- [ ] All function signatures have type hints (parameters + return type)
- [ ] f-strings used for interpolation (no `%` or `.format()`)
- [ ] No magic strings or numbers — use named constants
- [ ] `ruff check vigile.py` passes with no errors
- [ ] `ruff format --check vigile.py` passes (file is formatted)

## Functions & Naming

- [ ] Functions: verb-first names (`get_season`, `build_html`, `send_email`)
- [ ] Booleans: `is/has/should/can` prefix
- [ ] Constants: `UPPER_SNAKE_CASE`
- [ ] No function exceeds 30 lines

## GitHub Actions

- [ ] Cron syntax is valid (`0 13 1 * *`)
- [ ] All four secrets passed as env vars in `monthly_briefing.yml`
- [ ] CI workflow checks both `ruff check` and `ruff format --check`
- [ ] Secrets check job only runs on main branch

## Final Verification

```bash
ruff check vigile.py && ruff format --check vigile.py
```

Both commands must pass before committing.
