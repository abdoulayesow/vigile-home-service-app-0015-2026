# Anthropic Client Patterns

Project-grounded examples for Anthropic SDK usage in Vigile.

## Call Structure: Validate → Call → Handle Error → Return

Every Anthropic API call follows this sequence:

```python
def generate_brief(system_prompt: str, user_prompt: str) -> str:
    # 1. CALL — instantiate client (reads ANTHROPIC_API_KEY from env)
    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        # 2. EXTRACT — get text from response
        return message.content[0].text
    except Exception as e:
        # 3. HANDLE ERROR — print and exit
        print(f"Error calling Anthropic API: {e}")
        sys.exit(1)
```

## Client Initialization

The `anthropic.Anthropic()` constructor reads `ANTHROPIC_API_KEY` from the environment automatically. Validate the env var before calling the constructor:

```python
# Good — validate first, then let SDK read from env
required = ["ANTHROPIC_API_KEY", ...]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print(f"Error: missing required environment variables: {', '.join(missing)}")
    sys.exit(1)

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY already confirmed present
```

## System Prompt as Module Constant

The system prompt is a multi-line string constant at module level. Never build it dynamically:

```python
SYSTEM_PROMPT = """\
You are Vigile, a personal home guardian...

## Home Systems Inventory
...
"""
```

Keep the system prompt static — it encodes Ablo's home inventory which does not change at runtime.

## Dynamic User Prompt

The user prompt changes each month:

```python
user_prompt = (
    f"Generate Ablo's home maintenance brief for {month_name} {year}"
    f" ({season} in South Conroe, Texas)."
)
```

## Response Access

Access the text safely. `message.content` is a list; index 0 is the text block:

```python
brief_text = message.content[0].text
```

If Claude returns an empty response (rare), this raises `IndexError`. Guard if needed:

```python
if not message.content:
    print("Error: Anthropic API returned empty response")
    sys.exit(1)
brief_text = message.content[0].text
```

## Model Selection

Always use the exact model string from the project constant:

```python
CLAUDE_MODEL = "claude-sonnet-4-20250514"

message = client.messages.create(
    model=CLAUDE_MODEL,
    ...
)
```

Do not use `"claude-3-sonnet"` or other aliases — always use the full versioned model ID.
