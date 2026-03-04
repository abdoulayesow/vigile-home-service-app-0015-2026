# Vigile by Ablo — Automated Monthly Home Maintenance Briefing

Vigile by Ablo is a personal home guardian that emails a tailored, AI-generated maintenance brief
to your inbox on the 1st of every month. It runs fully automatically via GitHub Actions — no dashboards,
no logins, no effort required. It knows your home, your climate, your appliances, and your lawn
schedule, and tells you exactly what to do this month before problems happen.

---

## 1. Gmail App Password Setup

Vigile sends email via Gmail SMTP using an App Password (not your regular password). This
requires 2-Step Verification to be enabled on your Google account.

**Steps:**

1. Go to [myaccount.google.com](https://myaccount.google.com) and sign in.
2. Navigate to **Security** → **2-Step Verification** and enable it if not already on.
3. Return to **Security** and search for **App Passwords** (or go to
   [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
4. Click **Create** → enter a name (e.g., `Vigile`) → click **Create**.
5. Google shows a 16-character password. **Copy it immediately** — it won't be shown again.

This 16-character password is your `GMAIL_APP_PASSWORD` secret.

---

## 2. GitHub Secrets Setup

All credentials are stored as GitHub repository secrets — never in code.

**Steps:**

1. Go to your repository on GitHub.
2. Click **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
3. Add each of the following secrets:

**Required (email delivery):**

| Secret Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com) |
| `GMAIL_ADDRESS` | Your full Gmail address (e.g., `yourname@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character App Password from step above |
| `RECIPIENT_EMAILS` | Comma-separated list of recipient addresses (e.g., `you@gmail.com,partner@gmail.com`) |

**Optional — WhatsApp delivery** (see [Section 6](#6-optional-whatsapp-delivery)):

| Secret Name | Value |
|---|---|
| `WHATSAPP_TOKEN` | Meta permanent access token |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID from Meta dashboard |
| `WHATSAPP_RECIPIENTS` | Comma-separated recipient numbers in E.164 format (e.g., `+15551234567`) |

**Optional — Telegram delivery** (see [Section 7](#7-optional-telegram-delivery)):

| Secret Name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather (e.g., `123456:ABC-DEF...`) |
| `TELEGRAM_CHAT_IDS` | Comma-separated chat IDs (e.g., `123456789`) |

---

## 3. Local Test

Run Vigile locally to verify everything works before the first automated run.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GMAIL_ADDRESS="yourname@gmail.com"
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
export RECIPIENT_EMAILS="yourname@gmail.com"

pip install -r requirements.txt
python vigile.py
```

On success, you'll see:

```
Vigile brief sent for March 2026 to 1 recipient(s).
```

Check your inbox for the brief. If it lands in spam, mark it as "Not spam" — Gmail will learn.

---

## 4. Schedule

The automated workflow runs on the **1st of every month at 13:00 UTC (8:00 AM CST)**.

**Manual trigger:** Go to your repository → **Actions** → **Vigile Monthly Briefing** →
**Run workflow** → click the green button. Useful for testing after initial setup.

**Failure alerts:** If the script fails (API error, SMTP error, missing secret), GitHub Actions
marks the job red and sends you an email notification via your GitHub account preferences.

---

## 5. How It Works

1. GitHub Actions wakes up on the 1st of the month.
2. The script detects the current month and season (Spring/Summer/Fall/Winter).
3. It calls the Claude API with a full home systems inventory as context.
4. Claude generates a personalized 6-section brief (🔴 Urgent / 🟡 This Month / 🟢 Keep an Eye On / 💡 Blind Spot).
5. The brief is formatted as HTML and sent via Gmail SMTP to all `RECIPIENT_EMAILS`.
6. If configured, a condensed plain-text version is sent via WhatsApp and/or Telegram.

---

## 6. Optional — WhatsApp Delivery

Vigile can send a condensed brief (~1,000 chars) to WhatsApp using the **Meta Cloud API** (free
tier: 1,000 conversations/month — more than enough for a monthly brief).

> **Important:** WhatsApp Cloud API requires the recipient to have messaged your business number
> within the last 24 hours, OR you must use an approved message template. For personal/family use,
> the easiest approach is to send a quick "hi" to the business number each month before the 1st,
> or set up a simple approved template (takes ~1–2 days for Meta review).

**Setup steps:**

1. Go to [developers.facebook.com](https://developers.facebook.com) and create a free account.
2. Create a new app → select **Business** type.
3. Add the **WhatsApp** product to your app.
4. In **WhatsApp → API Setup**, note your:
   - **Phone Number ID** → this is your `WHATSAPP_PHONE_NUMBER_ID`
   - **Temporary access token** (valid 24h for testing) or generate a **permanent token** via
     System Users in Business Manager for production.
5. Add the test number or your real number as a recipient in the **To** field.
6. Recipient phone numbers must be in **E.164 format** (e.g., `+15551234567`).
7. Add the three secrets to your GitHub repo (see [Section 2](#2-github-secrets-setup)).

**Test locally:**

```bash
export WHATSAPP_TOKEN="EAAxxxxx..."
export WHATSAPP_PHONE_NUMBER_ID="1234567890"
export WHATSAPP_RECIPIENTS="+15551234567"
python vigile.py
```

On success: `WhatsApp sent to 1 recipient(s).`
If secrets are missing: `WhatsApp secrets not configured — skipping.` (non-fatal, email still sends)

---

## 7. Optional — Telegram Delivery

Vigile can send the full brief (up to 4,000 chars) to a Telegram chat using the **Telegram Bot
API** — completely free, no limits, no approval required.

**Setup steps:**

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts to name your bot.
3. BotFather gives you a token like `123456789:ABCdefGHI...` → this is your `TELEGRAM_BOT_TOKEN`.
4. Start a chat with your new bot (search its username and press **Start**).
5. Get your **chat ID**: visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
   after sending any message to the bot. Look for `"chat":{"id":XXXXXXX}` — that number is your
   `TELEGRAM_CHAT_IDS` value.
6. Add the two secrets to your GitHub repo (see [Section 2](#2-github-secrets-setup)).

For multiple recipients, add each person to a group chat and use the group's chat ID, or
comma-separate individual chat IDs: `123456789,987654321`.

**Test locally:**

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHI..."
export TELEGRAM_CHAT_IDS="123456789"
python vigile.py
```

On success: `Telegram sent to 1 chat(s).`
If secrets are missing: `Telegram secrets not configured — skipping.` (non-fatal, email still sends)
