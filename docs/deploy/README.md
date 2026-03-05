# Vigile by Ablo — Deployment Guide

This guide covers everything needed to go from a fresh repo clone to a fully
running Vigile installation: automated monthly email, WhatsApp/Telegram
delivery, and the personal dashboard on GitHub Pages.

---

## Prerequisites

- GitHub account (repo already exists)
- Gmail account with 2-Step Verification enabled
- Anthropic API account with credits

---

## Step 1 — Anthropic API Key

1. Log in at **console.anthropic.com**
2. Go to **API Keys** → **Create Key**
3. Copy the key — you'll add it as a repo secret in Step 4

---

## Step 2 — Gmail App Password

> Required because Vigile uses Gmail SMTP with `STARTTLS`. A regular Gmail
> password won't work — Google requires an App Password when 2-Step
> Verification is on.

1. Go to **myaccount.google.com → Security → 2-Step Verification** (enable it
   if not already on)
2. Search for **"App passwords"** in the Google Account search bar
3. Create a new app password — name it "Vigile"
4. Copy the 16-character password (no spaces)

---

## Step 3 — Create the Dashboard Gist

The monthly job writes the brief as JSON to a private GitHub Gist. The
dashboard reads it at runtime.

1. Go to **gist.github.com**
2. Click **"+"** (New gist)
3. Set **Filename** to exactly: `vigile-brief.json`
4. Add this placeholder as the content:
   ```json
   {}
   ```
5. Set visibility to **Secret** (not listed publicly)
6. Click **Create secret gist**
7. Copy the **Gist ID** from the URL:
   `https://gist.github.com/YOUR_USERNAME/`**`THIS_PART_IS_THE_ID`**

---

## Step 4 — Create a GitHub PAT for Gist Writes

The monthly job needs a token to update the Gist via the GitHub API.

1. Go to **github.com → Settings → Developer settings → Personal access
   tokens → Tokens (classic)**
2. Click **Generate new token (classic)**
3. Name it "Vigile Gist Write"
4. Set expiration (1 year recommended)
5. Check the **`gist`** scope only — nothing else needed
6. Click **Generate token** and copy it immediately

---

## Step 5 — Add All Repo Secrets

Go to your repo on GitHub → **Settings → Secrets and variables → Actions →
New repository secret**. Add each secret below.

### Required secrets

| Secret name         | Value                                      |
|---------------------|--------------------------------------------|
| `ANTHROPIC_API_KEY` | Key from Step 1                            |
| `GMAIL_ADDRESS`     | Your full Gmail address (e.g. `you@gmail.com`) |
| `GMAIL_APP_PASSWORD`| 16-char app password from Step 2           |
| `RECIPIENT_EMAILS`  | Comma-separated list of email recipients (e.g. `you@gmail.com,partner@example.com`) |

### Dashboard secrets (required for the dashboard to work)

| Secret name   | Value                            |
|---------------|----------------------------------|
| `GIST_TOKEN`  | PAT from Step 4                  |
| `GIST_ID`     | Gist ID from Step 3              |

### Optional delivery secrets

Leave these unset to skip the channel. The job will log "skipping" and continue.

| Secret name              | Value                                         |
|--------------------------|-----------------------------------------------|
| `WHATSAPP_TOKEN`         | Meta Cloud API bearer token                   |
| `WHATSAPP_PHONE_NUMBER_ID` | Phone number ID from Meta developer console |
| `WHATSAPP_RECIPIENTS`    | Comma-separated E.164 numbers (e.g. `+12815550100`) |
| `TELEGRAM_BOT_TOKEN`     | Token from @BotFather                         |
| `TELEGRAM_CHAT_IDS`      | Comma-separated chat IDs                      |

---

## Step 6 — Configure the Dashboard HTML

Open `docs/index.html` and find these two constants near the top of the
`<script>` block (around line 170):

```js
const GIST_OWNER = 'YOUR_GITHUB_USERNAME';
const GIST_ID    = 'YOUR_GIST_ID';
```

Replace both values with your actual GitHub username and the Gist ID from
Step 3:

```js
const GIST_OWNER = 'abdoulayesow';        // ← your GitHub username
const GIST_ID    = 'abc123def456...';     // ← your Gist ID
```

Commit and push this change.

---

## Step 7 — Enable GitHub Pages

1. Go to your repo on GitHub → **Settings → Pages**
2. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`
3. Click **Save**
4. GitHub will show the URL: `https://YOUR_USERNAME.github.io/REPO_NAME/`
   (it takes ~60 seconds to go live)

---

## Step 8 — Run a First Test

Trigger the monthly job manually to verify the full pipeline end-to-end:

1. Go to your repo → **Actions → Vigile Monthly Briefing**
2. Click **Run workflow → Run workflow**
3. Watch the job logs:
   - ✅ `Vigile brief sent for … to N recipient(s).`
   - ✅ `Brief saved to Gist for dashboard.`
   - ✅ WhatsApp/Telegram lines (or "skipping" if not configured)
4. Check your inbox — the HTML email should arrive
5. Open the GitHub Pages URL from Step 7
6. Enter your PIN (default: **`1234``) — change it after first login (see below)
7. The dashboard should load the brief from the Gist

---

## Step 9 — Change the Default PIN

The dashboard PIN is validated via SHA-256 — the raw PIN is never stored in
source. The default PIN is `1234`.

To set a new PIN:

1. **Compute the SHA-256 hash** of your chosen PIN:
   ```bash
   echo -n "YOUR_PIN" | sha256sum
   ```
   Example output: `03ac674216f3e15c761ee1a5e255f067953623c8ba1b64c3b7a4b6e8a8b80c39`

2. **Open `docs/index.html`** and find this constant (around line 175):
   ```js
   const PIN_HASH = '03ac674216f3e15c761ee1a5e255f067953623c8ba1b64c3b7a4b6e8a8b80c39';
   ```

3. Replace the hash string with your new hash

4. Commit and push — GitHub Pages updates within ~60 seconds

---

## Ongoing Schedule

The job runs automatically on the **1st of every month at 8:00 AM CST**
(cron: `0 13 1 * *` UTC). No action needed once deployed.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| CI fails with `secrets-check` error | A required secret is missing | Add the missing secret (Step 5) |
| Email not received | Wrong `GMAIL_APP_PASSWORD` | Regenerate the app password |
| "Gist save failed" in job logs | Wrong `GIST_TOKEN` or `GIST_ID` | Re-check Steps 3–5 |
| Dashboard shows "Setup required" | `GIST_OWNER`/`GIST_ID` not updated in HTML | Complete Step 6 |
| Dashboard shows "Could not load brief" | Gist is empty or token expired | Run workflow dispatch (Step 8), refresh PAT if expired |
| Dashboard loads but cards are empty | Brief not yet generated | Run workflow dispatch |
| Wrong PIN accepted | Old hash still in HTML | Follow Step 9 |
