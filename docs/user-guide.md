# Vigile User Guide

## What is Vigile

Vigile is your automated home maintenance assistant. On the 1st of every month, it sends you a
personalized email brief covering what needs attention around the house this month — from urgent
repairs to seasonal check-ins to easy-to-miss blind spots. It knows your home's systems, your
South Conroe climate, and the current season, so each brief is specific to you, not generic advice.
You set it up once and it runs on its own every month.

---

## One-Time Setup

### Step 1: Create a Gmail App Password

Gmail requires a special app password (separate from your regular Gmail password) to let Vigile
send email on your behalf.

1. Go to [myaccount.google.com](https://myaccount.google.com) and sign in
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google," click **2-Step Verification** (you must have this enabled)
4. Scroll to the bottom and click **App passwords**
5. Under "App name," type `Vigile` and click **Create**
6. Google shows a **16-character password** (e.g., `abcd efgh ijkl mnop`) — copy it now
   > You will not be able to see this password again. Paste it somewhere safe temporarily.

---

### Step 2: Add Secrets to GitHub

Vigile reads four secrets from your GitHub repository. These are stored securely and never visible
in logs or code.

1. Go to your Vigile repository on GitHub
2. Click **Settings** (top navigation bar)
3. In the left sidebar, click **Secrets and variables → Actions**
4. Click **New repository secret** for each of the following:

| Secret name | Value to enter |
|---|---|
| `ANTHROPIC_API_KEY` | Your API key from [console.anthropic.com](https://console.anthropic.com) |
| `GMAIL_ADDRESS` | Your full Gmail address (e.g., `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character app password from Step 1 |
| `RECIPIENT_EMAILS` | Email address(es) to receive the brief — separate multiple with commas |

> **Tip:** If you want the brief sent to more than one address, enter them comma-separated:
> `you@gmail.com,spouse@gmail.com`

That's it. Vigile will now run automatically every month.

---

## WhatsApp Setup *(optional — v1.1)*

In addition to email, Vigile can send your monthly brief as a WhatsApp message. This is optional —
email delivery works without it.

### What you need

- A Twilio account — sign up at [twilio.com](https://www.twilio.com) (free trial available)
- Your phone number enrolled in the Twilio WhatsApp Sandbox (one-time step)

### Step-by-step

1. **Create a Twilio account** at twilio.com and verify your phone number
2. In the Twilio Console, go to **Messaging → Try it out → Send a WhatsApp message**
3. Follow the sandbox instructions: send the join code from your WhatsApp to the Twilio number shown
4. Once joined, note your **Account SID** and **Auth Token** from the Twilio Console dashboard
5. Note the **Twilio WhatsApp sender number** (format: `whatsapp:+14155238886`)
6. Add four new GitHub Secrets to your repository (same process as before — Settings → Secrets and variables → Actions):

| Secret name | Value to enter |
|---|---|
| `TWILIO_ACCOUNT_SID` | From Twilio Console dashboard |
| `TWILIO_AUTH_TOKEN` | From Twilio Console dashboard |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp number, e.g. `whatsapp:+14155238886` |
| `WHATSAPP_RECIPIENTS` | Your number(s) with country code, e.g. `whatsapp:+12815550000` — separate multiple with commas |

> **Note:** The WhatsApp brief is plain text (no colors or formatting). It contains the same
> information as the email.

---

## Schedule

Vigile runs automatically on the **1st of every month at 8:00 AM CST** (13:00 UTC).

You do not need to do anything. On the 1st, check your inbox for an email with the subject line:

> 🏠 Vigile — [Month] [Year] Home Brief

---

## Manual Trigger

You can send a brief at any time — useful for testing or if you want an extra run mid-month.

1. Go to your Vigile repository on GitHub
2. Click the **Actions** tab (top navigation)
3. In the left sidebar, click **Vigile Monthly Briefing**
4. Click the **Run workflow** dropdown on the right
5. Click the green **Run workflow** button

The brief will arrive in your inbox within a minute or two.

---

## Reading the Brief

Each brief has four labeled sections. Here is what the markers mean:

| Marker | Meaning |
|---|---|
| 🔴 **Urgent** | Do this now — waiting could cause damage or a safety issue |
| 🟡 **This Month** | Schedule or handle this during the current month |
| 🟢 **Keep an Eye On** | Nothing urgent, but worth checking or monitoring |
| 💡 **Blind Spot** | Easy-to-forget item that often gets missed until it becomes a problem |

Each section lists specific tasks for your home based on the current month and season in South
Conroe, TX. The brief always ends with a short closing note.

---

## Troubleshooting

**No email arrived on the 1st**

1. Go to your repository on GitHub and click the **Actions** tab
2. Look for the most recent **Vigile Monthly Briefing** run
3. If the run shows a red X, click it to see the error details
4. Common causes:
   - A secret is missing or was entered incorrectly — re-add it under Settings → Secrets and variables → Actions
   - The Gmail App Password was invalidated — generate a new one and update `GMAIL_APP_PASSWORD`
   - The Anthropic API key expired or has no credits — check [console.anthropic.com](https://console.anthropic.com)

**Email went to spam**

Mark the email as "Not spam" and add the sending address to your contacts. This trains Gmail to
deliver future briefs to your inbox.

**The brief arrived but looks broken (no formatting)**

Your email client may not support HTML. The brief includes a plain-text version as well — it
contains the same information, just without visual styling.

**Email arrived but no WhatsApp message**

1. Go to the Actions tab and check the run logs for any Twilio error
2. Common causes:
   - Your phone number is not enrolled in the Twilio sandbox — re-send the join code from WhatsApp
   - `TWILIO_WHATSAPP_FROM` or `WHATSAPP_RECIPIENTS` is missing the `whatsapp:` prefix
   - Twilio trial account credits exhausted — add funds or upgrade the account
3. WhatsApp failures are logged separately and do not affect email delivery
