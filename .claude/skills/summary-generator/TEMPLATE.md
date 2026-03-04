# Session Summary Templates

Two tiers: **Lean** for short/narrow sessions, **Full** for substantial work.

---

## Lean Template

For commits, config changes, quick fixes, single bug fixes.

```markdown
# Session Summary: [FEATURE_NAME]

**Date:** YYYY-MM-DD HH:MM
**Session Focus:** [one-line description]

## Completed Work

- [bullet]
- [bullet]

## Key Files Modified

| File | Changes |
|------|---------|
| `vigile.py` | [brief description] |

## Current State

[git status: what's committed vs pending, branch state]

## Next Steps

1. [next task]
2. [following task]

## Mistakes & Learnings

[Only if there were failed commands, retries, or avoidable mistakes]

- **[mistake]** → Fix: [what worked]. Saved to memory: [yes/no]

## Resume Prompt

` ` `
Resume [FEATURE_NAME] session.

## Context
Previous session completed:
- [key accomplishment 1]
- [key accomplishment 2]

Session summary: .claude/summaries/YYYY-MM-DD/YYYY-MM-DDTHH-MM_feature-name.md

## Key Files to Review First
- vigile.py (primary changes)

## Current Status
[brief status]

## Next Steps
1. [immediate next task]
2. [following task]
` ` `
```

---

## Full Template

For feature implementation, refactors, multi-step work.

```markdown
# Session Summary: [FEATURE_NAME]

**Date:** YYYY-MM-DD HH:MM
**Session Focus:** [brief description]

## Overview

[1-2 paragraph summary of goals and outcomes]

## Completed Work

### [Category 1 — e.g., "Core Script"]
- [specific accomplishment]

### [Category 2 — e.g., "GitHub Actions"]
- [specific accomplishment]

## Key Files Modified

| File | Changes |
|------|---------|
| `vigile.py` | [brief description] |
| `.github/workflows/monthly_briefing.yml` | [brief description] |

## Design Patterns Used

- **[Pattern Name]**: [how applied and why]

## Plan Progress

| Task | Status | Notes |
|------|--------|-------|
| Task 1 | **COMPLETED** | [notes] |
| Task 2 | **PENDING** | [what remains] |

## Next Steps

1. [next task with context]
2. [following task]

### Blockers or Decisions Needed
- [any blockers discovered]

## Session Retrospective

**Efficiency:** [Good / Fair / Poor] — [1-sentence justification]

### What Went Well
- [bullet]

### What Could Improve
- [bullet]

### Notable Issues
- [only if there were actual errors/failures worth documenting]

## Lessons Learned

- [pattern or insight worth remembering]

## Mistakes & Learnings

[Review failed commands, ruff errors, and retries from this session]

| Mistake | Root Cause | Fix | Saved to Memory? |
|---------|-----------|-----|------------------|
| [failed command/error] | [why it happened] | [what worked] | [yes — file.md / no — one-off] |

## Resume Prompt

` ` `
Resume [FEATURE_NAME] session.

## Context
Previous session completed:
- [key accomplishment 1]
- [key accomplishment 2]
- [key accomplishment 3]

Session summary: .claude/summaries/YYYY-MM-DD/YYYY-MM-DDTHH-MM_feature-name.md

## Key Files to Review First
- vigile.py (primary changes)
- .github/workflows/monthly_briefing.yml (workflow)

## Current Status
[brief status statement]

## Next Steps
1. [immediate next task]
2. [following task]
3. [third task]

## Important Notes
- [critical context]
- [blockers or decisions needed]
` ` `
```

---

## Template Tips

1. **Feature Name**: Use kebab-case for the filename (e.g., `vigile-initial-build`)
2. **Completed Work**: Group by category for easier scanning
3. **Files Table**: Include only files with significant changes
4. **Resume Prompt**: Make it copy-paste ready for the next session
5. **Retrospective**: Be honest — don't fabricate metrics you can't measure
