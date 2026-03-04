# Token Efficiency Guidelines

Reduce token usage while maintaining quality. Efficiency = maximizing value per token.

## Core Rules

1. **Search before reading** — Use Grep/Glob to find what you need, then Read targeted sections
2. **Read once, reference later** — Don't re-read files you've already seen; reference conversation context
3. **Be concise** — Bullets over paragraphs, explain "why" not "what"
4. **Combine operations** — Use glob patterns (`**/*.py`) and regex alternation
5. **Use agents for complex exploration** — One Explore agent spawn beats 10 manual searches

## File Operations

**Do:**
- `Grep pattern="def send_email" path="vigile.py"` then `Read vigile.py offset=50 limit=20`
- Use `offset`/`limit` for large files
- Trust earlier reads — only re-read if the file may have changed

**Don't:**
- Read the same file multiple times
- Read entire files when Grep answers the question
- Read generated files or caches

## Search Operations

**Do:**
- `Glob pattern="**/*.py"` (one search for all Python files)
- `Grep pattern="import.*(anthropic|smtplib)" path="vigile.py"` (one search, not two)
- Scope searches to relevant directories and file types

**Don't:**
- Run sequential similar globs/greps that could be combined
- Search the entire repo when `vigile.py` is the only source file

## Responses

**Do:**
- `"Fixed import: 'anthropic.Client' → 'anthropic.Anthropic'"` (~15 tokens)
- Explain decisions, not actions — tool calls are self-evident

**Don't:**
- Multi-paragraph explanations for simple changes (~100+ tokens wasted)
- Re-explain concepts already established in conversation
- Narrate each tool call before making it

## Code Generation

**Do:**
- Read function signatures first, generate complete correct code in one pass
- Include all imports and type hints — no placeholders

**Don't:**
- Generate incrementally (signature, then body, then types)
- Guess at function signatures then fix errors — read definitions first

## Planning

**Do:**
- Understand requirements → ask questions → plan → implement
- Reference CLAUDE.md and project docs already in context

**Don't:**
- Trial-and-error coding (generate → ruff error → fix → ruff error → fix)
- Re-establish information that's already known

## Quick Checklist

- [ ] Used Grep before Read when searching
- [ ] Avoided re-reading the same file
- [ ] Combined similar search patterns
- [ ] Scoped searches to `vigile.py` and `.github/` when appropriate
- [ ] Kept responses concise
- [ ] Read function signatures before generating code
- [ ] Referenced earlier context instead of re-reading
