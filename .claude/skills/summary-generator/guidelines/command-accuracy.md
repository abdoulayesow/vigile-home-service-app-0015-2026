# Command Accuracy Guidelines

Get it right the first time through verification and pattern-matching.

## Core Rules

1. **Verify before executing** — Check assumptions before running commands
2. **Follow existing patterns** — Match what already works in the codebase
3. **Read definitions first** — Understand functions/constants before implementing
4. **Use forward slashes** — Always, even on Windows
5. **Test incrementally** — Validate each step before proceeding

## Path Accuracy

**Do:**
- Use forward slashes: `vigile.py`, `.github/workflows/monthly_briefing.yml`
- Verify paths exist: `Glob pattern="**/*.py"` then `Read`
- Match exact case from Glob results (Linux is case-sensitive)

**Don't:**
- Use backslashes: `.github\workflows\monthly_briefing.yml`
- Assume paths without checking
- Guess case: `Vigile.py` vs `vigile.py`

## Import Accuracy

**Do:**
- Grep for existing imports first: `Grep pattern="import anthropic" path="vigile.py"`
- Verify module names before importing (`anthropic`, not `anthropic_sdk`)
- Match the import style used in the existing file

**Don't:**
- Guess import paths without verification
- Mix `import anthropic` with `from anthropic import Anthropic` inconsistently

## Type Safety

**Do:**
- Read function signatures before calling them
- Check how constants are defined (type, value)
- Match parameter names exactly from existing code

**Don't:**
- Guess function signatures
- Assume parameter order without reading the definition

## Edit Tool

**Do:**
- Read the file immediately before editing
- Copy `old_string` exactly from Read output (including whitespace)
- Include enough surrounding context to make the match unique

**Don't:**
- Change indentation in `old_string` (4 spaces vs 2 spaces = "string not found")
- Edit without reading first
- Use too-short `old_string` that matches multiple locations

## Regex / Grep

**Do:**
- Escape special characters: `Grep pattern="list\\[str\\]"`
- Build patterns incrementally: start simple, add specificity
- Use appropriate file type filters (`type="py"`)

**Don't:**
- Use unescaped brackets/parens in patterns
- Write overly complex regex when simple patterns suffice

## Pre-Execution Checklist

**Read/Edit/Write:**
- [ ] Path uses forward slashes
- [ ] File/directory exists (verified with Glob)
- [ ] Case matches exactly

**Edit specifically:**
- [ ] Recently read the file
- [ ] `old_string` copied exactly from Read output
- [ ] `old_string` is unique in the file

**Python/Imports:**
- [ ] Checked existing imports in `vigile.py`
- [ ] Read function/constant definitions
- [ ] Verified parameter names exist

## Recovery

When a command fails:
1. Read the error message — it usually tells you exactly what's wrong
2. Verify your assumptions (path exists? correct case? right parameter name?)
3. Check existing patterns in `vigile.py`
4. Fix and move on — don't repeat the same mistake
