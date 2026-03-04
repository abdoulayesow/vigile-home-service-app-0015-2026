# Vigile — Automated Monthly Home Maintenance Briefing

Vigile is a personal home guardian that emails a tailored, AI-generated maintenance brief to your
inbox on the 1st of every month. It runs fully automatically via GitHub Actions — no dashboards,
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

| Secret Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key from [console.anthropic.com](https://console.anthropic.com) |
| `GMAIL_ADDRESS` | Your full Gmail address (e.g., `yourname@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character App Password from step above |
| `RECIPIENT_EMAILS` | Comma-separated list of recipient addresses (e.g., `you@gmail.com,partner@gmail.com`) |

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
