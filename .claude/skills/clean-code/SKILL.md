---
name: clean-code
description: Analyzes code against clean code standards and produces refactoring recommendations. Use when refactoring, cleaning up code, or checking code quality. Trigger with "clean up", "refactor", "clean code", "code quality".
allowed-tools: Read, Glob, Grep, Bash(ruff check vigile.py), Bash(ruff format --check vigile.py), Bash(python -m pytest)
---

# Clean Code Analysis & Refactoring Skill

## Overview

This skill analyzes Python source code against the project's clean code standards and produces actionable refactoring recommendations. It identifies violations, suggests specific fixes with before/after examples, and grades overall code health.

## When to Use

- User explicitly requests cleanup: "clean up", "refactor", "clean code", "code quality"
- After completing a feature (pre-commit quality check)
- When reviewing code written by others or AI agents
- When `vigile.py` grows beyond 200 lines

### Auto-Suggest Triggers

Proactively suggest running this skill when:
- A function exceeds 30 lines after edits
- Logic is duplicated across functions
- Magic strings or numbers appear in new code
- A function has more than 3 parameters

## Instructions

### Step 1: Identify Target Files

Determine which files to analyze:
- If the user specifies files, use those
- Otherwise, check recent changes: `git diff --name-only`
- For full audit, analyze `vigile.py`

### Step 2: Analyze Against Rules

Check each file against the **All Rules** section below. Reference the detailed guidelines in `guidelines/` for project-specific patterns and examples.

### Step 3: Check Refactoring Triggers

Review `checklists/refactoring-triggers.md` to identify structural improvements.

### Step 4: Produce Report

Output a structured report using the **Output Format** below.

### Step 5: Suggest Specific Fixes

For each issue, provide:
- File path and line number
- The rule being violated
- Before/after code snippet
- Severity (Critical / High / Medium / Low)

## All Rules

### Python Style
- Follow PEP 8; enforce with `ruff check` (default rules: E4, E7, E9, F)
- Use `ruff format` for consistent formatting (88-char line length, double quotes)
- No `# type: ignore` unless absolutely necessary with a comment explaining why
- Use f-strings for string interpolation; avoid `%` formatting or `.format()`

### Type Hints
- All function signatures must have type hints (parameters + return type)
- Use `list[str]` not `List[str]` (Python 3.9+ built-in generics)
- Use `str | None` not `Optional[str]` (Python 3.10+ union syntax)
- Use `Any` only with explicit justification comment

### Functions
- Functions do one thing; name with verb-first (`get_season`, `build_html`, `send_email`)
- Max 3 parameters; use a dataclass or dict for more
- Guard clauses at the top; return early for error cases
- Functions over 30 lines should be refactored

### Constants
- Module-level constants in `UPPER_SNAKE_CASE`
- No magic strings or numbers inline — extract to named constants
- Group related constants together (e.g., `SECTION_COLORS`, `MONTH_NAMES`)

### Error Handling
- Wrap all external calls (API, SMTP) in `try/except Exception as e`
- Print a clear human-readable error message before `sys.exit(1)`
- Never print raw secret values in error messages
- Validate inputs at system boundaries (env vars); trust internal data

### Security
- All secrets from `os.getenv()` or `os.environ` — never hardcoded
- Never include credential values in print/log output
- HTML-escape user-facing content with `html.escape()`

### Testing
- Test behavior, not implementation; name tests with "test_" prefix
- AAA pattern: Arrange (setup/mocks) → Act (call function) → Assert (verify result)
- Mock at module boundaries with `unittest.mock.patch`
- Use `pytest` for test runner

### Code Organization
- Module-level: imports → constants → functions → `if __name__ == "__main__"`
- 2 blank lines between top-level definitions
- Imports: stdlib first, then third-party (`anthropic`), separated by blank line

## Output Format

```markdown
## Clean Code Analysis: [target description]

### Summary
[1-2 sentence overall assessment with letter grade A-F]

### Critical Issues
[Security vulnerabilities, hardcoded secrets, breaking patterns]

### High Priority
[Logic errors, missing error handling, type safety violations]

### Medium Priority
[Naming violations, missing constants, code organization]

### Recommendations
[Refactoring suggestions with before/after snippets]

### Positive Notes
[Patterns followed well, good practices observed]
```
