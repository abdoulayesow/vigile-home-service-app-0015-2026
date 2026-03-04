---
name: summary-generator
description: Generates session summaries and resume prompts for multi-session work. Use when completing features, before context limits (~50% capacity), or when user says "summary", "wrap up", "save progress", "end session". Creates markdown in .claude/summaries/ with completed work, files modified, and restart instructions.
allowed-tools: Read, Edit, Glob, Grep, Bash(git diff:*), Bash(git log:*), Bash(git status:*), Write
---

# Session Summary Generator

## Overview

Creates session summaries for multi-session work, enabling seamless resumption. Generates a markdown file in `.claude/summaries/YYYY-MM-DD/` with a standardized format.

## When to Use

- User requests a summary ("generate summary", "wrap up", "save progress")
- Completing a significant feature or refactor
- Conversation context reaching limits (~50% before auto-compact)
- Before starting a new chat session

## Output Location

```
.claude/summaries/YYYY-MM-DD/YYYY-MM-DDTHH-MM_feature-name.md
```

- **Folder**: date portion of the filename
- **Filename**: `YYYY-MM-DDTHH-MM_kebab-feature-name.md` (time from current timestamp, `-` instead of `:` for filesystem safety)

## Template Tiers

Choose the template based on session scope:

### Lean Summary
Use when the session was short or narrowly scoped: commits, config changes, quick fixes, single bug fixes.

### Full Summary
Use for feature implementation, refactors, multi-step work, or sessions with significant design decisions.

See [TEMPLATE.md](TEMPLATE.md) for both templates.

## Guidelines

Follow these when gathering information and generating the summary:

- **Token efficiency** (`guidelines/token-efficiency.md`): Search before reading, combine operations, scope searches to relevant dirs, don't re-read files already in context. Keep summary prose concise — bullets over paragraphs.
- **Command accuracy** (`guidelines/command-accuracy.md`): Use forward slashes in all paths, verify paths with Glob before referencing them in the summary, copy exact file paths from tool output.

## Instructions

### Step 1: Analyze Current Work

Run these commands to understand what was done:

```bash
git status
git diff --stat
git log --oneline -10
```

Review the conversation history to identify:
- What was accomplished
- Key decisions made
- Files created or modified
- Remaining tasks

### Step 2: Choose Template Tier

- **Lean**: Short session, narrow scope, few files changed
- **Full**: Feature work, refactors, architectural decisions, many files touched

### Step 3: Generate Summary File

Create the summary using the appropriate template from [TEMPLATE.md](TEMPLATE.md).

### Step 4: Create Resume Prompt

The resume prompt should be copy-paste ready and include:
- Context reference to the summary file
- Specific file paths to review first
- Current status and immediate next steps
- Any blockers or decisions needing user input

### Step 5: Session Retrospective (Full template only)

Provide an honest, qualitative assessment:
- **Efficiency**: Good / Fair / Poor with one-sentence justification
- **What went well**: bullets
- **What could improve**: bullets
- **Notable issues**: only if there were actual errors/failures

Do not fabricate token counts, command totals, or scoring numbers. If you can't measure it, don't report it.

### Step 6: Self-Reflection & Memory Update

Review the session for recurring mistakes and persist learnings to auto memory. This step runs for **both** Lean and Full summaries.

**What to look for:**
- Commands that failed and had to be retried (wrong flags, missing env vars, bad paths)
- ruff or Python errors that required multiple fix attempts
- Patterns you discovered mid-session that would have saved time if known upfront
- Workarounds for platform/tooling quirks (e.g., Windows path issues, pip behavior)

**What to do:**
1. Scan conversation for failed tool calls, error outputs, and retry patterns
2. For each recurring or avoidable mistake, check if it's already in auto memory (`MEMORY.md` or topic files like `debugging.md`, `patterns.md`)
3. If not already recorded, write it to the appropriate memory file — concise, actionable, with the fix
4. If an existing memory entry is wrong or outdated, update or remove it

**What NOT to save:**
- One-off typos or trivial mistakes that won't recur
- Session-specific context (current task details, temporary state)
- Anything that duplicates CLAUDE.md instructions

## Example Usage

When user says: "Let's wrap up for today"

1. Analyze git changes and conversation history
2. Create `.claude/summaries/2026-03-04/2026-03-04T14-30_vigile-initial-build.md`
3. Provide the resume prompt
4. Suggest: "When context gets long, start a new chat with this resume prompt"

## Tips

- Keep summaries focused on a single feature or area
- Include exact file paths for easy navigation
- Note any environmental setup needed (env vars, pip install)
- Flag any blocking issues or decisions made
- Reference the CLAUDE.md file patterns when applicable
