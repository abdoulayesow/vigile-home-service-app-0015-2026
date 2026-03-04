# Vigile Testing Guide

## Prerequisites

- Python 3.12 or later
- Core packages: `pip install anthropic`
- WhatsApp (optional): `pip install twilio` — only needed if testing WhatsApp delivery
- Four core environment variables (see Local End-to-End Test below)
- A Gmail account with 2-Step Verification enabled and an App Password generated
- For WhatsApp: a Twilio account with your number enrolled in the WhatsApp Sandbox

---

## Local End-to-End Test

Set the four required environment variables, then run the script directly:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
export RECIPIENT_EMAILS="you@gmail.com"

python vigile.py
```

**Expected output:**

```
Vigile brief sent for March 2026 to 1 recipient(s).
```

Check your inbox for an email with the subject `🏠 Vigile — March 2026 Home Brief`. The script
exits with code `0` on success.

> **Note:** Running the script locally uses real API credits and sends a real email. Use your own
> address as `RECIPIENT_EMAILS` during testing.

---

## WhatsApp End-to-End Test *(v1.1)*

Set the four core variables plus the four Twilio variables, then run the script:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
export RECIPIENT_EMAILS="you@gmail.com"
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"
export WHATSAPP_RECIPIENTS="whatsapp:+12815550000"

python vigile.py
```

**Expected output:**

```
Vigile brief sent for March 2026 to 1 recipient(s).
WhatsApp brief sent to 1 recipient(s).
```

Check your WhatsApp for a message from the Twilio sandbox number containing the plain-text brief.

> **Note:** If the Twilio env vars are not set, WhatsApp delivery is skipped silently. Email
> delivery always runs regardless of WhatsApp configuration.

### WhatsApp error path tests

**Missing or invalid Twilio credentials**

```bash
export TWILIO_ACCOUNT_SID="invalid"
python vigile.py
# Expected: email sends successfully, WhatsApp logs a Twilio error, exits 0
# (WhatsApp failure is non-fatal — email is the primary delivery channel)
```

**Recipient not enrolled in sandbox**

Send the Twilio sandbox join code from your WhatsApp before testing. If you receive a 63016 error
in the logs, your number is not enrolled.

---

## Error Path Tests

Each of these tests verifies that the script fails fast and clearly when a secret is missing or
wrong, and exits with code `1` (which marks the GitHub Actions job red).

### Missing ANTHROPIC_API_KEY

```bash
unset ANTHROPIC_API_KEY
python vigile.py
# Expected: prints authentication error message, exits 1
```

### Invalid ANTHROPIC_API_KEY

```bash
export ANTHROPIC_API_KEY="sk-ant-invalid"
python vigile.py
# Expected: prints Anthropic AuthenticationError, exits 1
```

### Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD

```bash
unset GMAIL_ADDRESS
python vigile.py
# Expected: prints missing env var message, exits 1
```

### Invalid GMAIL_APP_PASSWORD

```bash
export GMAIL_APP_PASSWORD="wrong-password"
python vigile.py
# Expected: prints SMTPAuthenticationError, exits 1
```

### Missing RECIPIENT_EMAILS

```bash
unset RECIPIENT_EMAILS
python vigile.py
# Expected: prints missing env var message, exits 1
```

After each test, restore the correct values before continuing.

---

## Manual Workflow Dispatch

To trigger a run directly from GitHub Actions without waiting for the scheduled cron:

1. Go to the repository on GitHub
2. Click the **Actions** tab
3. In the left sidebar, click **Vigile Monthly Briefing**
4. Click the **Run workflow** dropdown (top right of the run list)
5. Click the green **Run workflow** button
6. Refresh the page — a new run appears at the top with a yellow spinner
7. Click the run to watch live logs; the job should complete green within ~30 seconds

A successful run ends with the step output:

```
Vigile brief sent for [Month] [Year] to N recipient(s).
```

---

## CI Verification

The CI workflow runs `ruff` lint and format checks on every push. To run the same checks locally
before pushing:

```bash
pip install ruff

# Lint check (catches errors and style violations)
ruff check vigile.py

# Format check (non-destructive — reports diff only, does not modify files)
ruff format --check vigile.py
```

**Both commands should produce no output and exit with code `0`.**

To auto-fix formatting issues (modifies the file in place):

```bash
ruff format vigile.py
```

---

## Email Output Checklist

After a successful run (local or via Actions), verify the email against this checklist:

**Subject line**
- [ ] Subject is `🏠 Vigile — [Month] [Year] Home Brief`
- [ ] Month and year match the current date

**HTML rendering**
- [ ] Email renders with styled section cards (not raw text)
- [ ] All four section markers present: 🔴 Urgent, 🟡 This Month, 🟢 Keep an Eye On, 💡 Blind Spot
- [ ] Closing nudge line appears at the end

**Content accuracy**
- [ ] Month name in the greeting matches the current month
- [ ] Season referenced matches South Conroe, TX expectations (e.g., "Spring" for March–May)
- [ ] Tasks are home-specific (HVAC, lawn, plumbing, etc.) — not generic filler

**Plain-text fallback**
- [ ] View the email in a plain-text client or "view original" mode
- [ ] All four sections present in plain text
- [ ] No HTML tags visible in the plain-text part

**WhatsApp message (if configured)**
- [ ] Message received from Twilio sandbox number
- [ ] Contains all four sections (🔴 🟡 🟢 💡)
- [ ] Month and season correct
- [ ] No HTML markup visible — plain text only
