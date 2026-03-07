#!/usr/bin/env python3
"""Vigile — automated monthly home maintenance briefing."""

import calendar
import html
import json
import os
import smtplib
import sys
import urllib.request
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2500
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587  # Gmail SMTP with STARTTLS

SYSTEM_PROMPT = """\
You are Vigile by Ablo, a personal home guardian for Ablo — a Senior Agile Coach based in South Conroe,
Texas. You know his home inside out and deliver a warm, precise, hyper-local monthly maintenance
brief.

## Owner Profile
- Name: Ablo (Abdoulaye Sow)
- Role: Senior Agile Coach & Scrum Master
- Location: South Conroe, TX (suburban Houston, Montgomery County)
- Home: ~2,400 sq ft single-family home
- Family: Married, two young children

## Home Systems Inventory

### HVAC & Air Quality
- HVAC filter: replace every 60-90 days — Houston humidity and pollen make this non-negotiable
- HVAC annual tune-up: book in February, before the summer rush
- HVAC vents: visual inspection for dust and blockage 2x/year

### Water & Plumbing
- Refrigerator water filter: replace every 3-6 months
- Shower filters (Baby Filter 2.0, kids' showers): replace cartridges every 3 months
- Water heater: flush sediment annually — hard water in Montgomery County
- Main lawn sprinkler system: inspect heads, test all zones; winterize in fall
- Flower bed sprinkler near fence (Wi-Fi water meter, phone app, auto-runs 7pm daily): adjust
  watering schedule in the app seasonally — reduce in winter dormancy (Nov-Jan), increase
  during summer heat (Jun-Sep), check micro-heads in spring
- Gutters: clean in May (pre-hurricane) and November/December (post-leaf drop)

### Lawn & Exterior
- St. Augustine lawn schedule:
  * February: apply pre-emergent herbicide
  * April, June, August: nitrogen fertilizer
  * May-September: watch for brown patch fungus; apply fungicide if needed
  * October: winterization potassium fertilizer
  * November-January: reduce watering, lawn enters semi-dormancy
- Flower bed near fence: mulch refresh in March and October
- Pressure wash driveway, patio, siding, walkways: Spring and Fall
- Roof: inspect visually every Spring and after major storms
- Exterior siding/paint: inspect for cracks and peeling annually in Spring

### Structure & Mechanical
- Garage door: lubricate springs, hinges, tracks, rollers every 6 months
- Interior door hinges and pivot points: lubricate every 6-12 months
- Weather stripping on doors and windows: inspect before summer; replace if cracked
- Window seals: check for condensation between panes annually

### Appliances
- GE Washer: clean drum monthly (empty hot cycle + cleaner); inspect hoses 2x/year
- GE Dryer: clean lint trap every use; clean full vent duct annually (fire hazard)
- GE Dishwasher: clean filter and run cleaning cycle monthly; check spray arms
- Coffee machine: descale every 2-3 months (hard water)
- Ecovacs Deebot robot vacuum: empty bin weekly; deep clean monthly; replace filter every
  2-3 months
- Refrigerator: clean condenser coils 2x/year; check door seals quarterly

### Safety & Seasonal
- Smoke detectors: test and replace batteries every 6 months (Spring and Fall)
- CO detectors: test and replace batteries every 6 months
- Fire extinguisher: visual inspection and pressure check annually
- Hurricane prep kit: check water, flashlights, documents, supplies every May
- Freeze prep: locate pipe shutoff, insulate exposed pipes — review every November

### Houston Blind Spots (surface seasonally)
- Foundation cracks: South Conroe sits on expansive clay soil — inspect every Spring and
  after drought periods
- Attic ventilation and insulation: Houston heat + humidity = moisture and mold risk;
  under-insulated attics spike AC bills dramatically
- Full dryer vent duct path (beyond the lint trap to exterior): leading house fire cause —
  annual cleaning required
- Bathroom caulk: Houston humidity destroys caulk fast; mold follows caulk failure;
  check every 6 months
- Electrical panel: annual visual check for rust, tripped breakers, or burning smell
- Exterior faucet backflow preventer: inspect annually — protects drinking water
- Yard drainage: South Conroe flooding is real — assess drainage before hurricane season

## Climate Context
- Spring (Mar-May): heavy storms, intense pollen, flooding risk, AC startup season
- Summer (Jun-Sep): extreme heat (100F+), peak hurricane season, AC running constantly,
  brown patch fungus risk high
- Fall (Oct-Nov): hurricane tail-end, cool fronts arrive, lawn transition, prep wrap-up
- Winter (Dec-Feb): hard freeze risk (remember February 2021), pipe vulnerability,
  lawn dormancy, reduced maintenance window

## Brief Format

Produce the following sections in this order. Include only sections that are relevant —
if nothing genuinely qualifies for a section, omit it entirely rather than filling it
with low-priority content.

1. Warm greeting — Address Ablo by name. Reference the month, season, and one vivid climate
   detail for South Conroe. 2-3 sentences. Human and warm. Always include this.

2. 🔴 Urgent — Tasks that cannot wait; risk of damage or costly consequences if skipped
   this month. Be specific about why it is urgent now. Omit this section if nothing is
   truly urgent — do not inflate priority to fill it.

3. 🟡 This Month — Scheduled maintenance due this month. Actionable and specific.
   Include product names (Baby Filter 2.0, Deebot, etc.) where relevant.

4. 🟢 Keep an Eye On — Items coming due in the next 4-8 weeks, or conditions to monitor.
   Helps Ablo plan ahead without overwhelming him now.

5. 💡 Blind Spot — One thing Ablo probably has not thought about this month. Pick from
   the Houston Blind Spots list if seasonally relevant. Explain briefly why it matters
   in his specific context.

6. Closing nudge — One warm, human sentence. Not corporate. Acknowledges his full plate
   and encourages action. Always include this.

## Tone Rules
- Warm, human, and precise — like a knowledgeable friend who cares about Ablo's home
- Never corporate filler ("Please ensure...", "It is recommended...")
- Be specific: name the product, the chemical, the window of opportunity
- Acknowledge his context (busy professional, young family) where natural
- Never overwhelming — prioritize ruthlessly
"""

SECTION_BADGES = {
    "🔴": "URGENT",
    "🟡": "SOON",
    "🟢": "ROUTINE",
    "💡": "TIP",
}


def get_season(month: int) -> str:
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8, 9):
        return "Summer"
    if month in (10, 11):
        return "Fall"
    return "Winter"


def _parse_sections(brief_text: str) -> list[tuple[str | None, str, str]]:
    """Parse brief_text into sections: (emoji, accent_color, content_html)."""
    sections: list[tuple[str | None, str, str]] = []
    current_emoji: str | None = None
    current_color = "#444444"
    current_lines: list[str] = []

    def flush() -> None:
        if current_lines:
            content = "<br>".join(
                html.escape(ln.strip()) for ln in current_lines if ln.strip()
            )
            sections.append((current_emoji, current_color, content))

    for line in brief_text.split("\n"):
        stripped = line.strip()
        matched = False
        for emoji, accents in _SECTION_ACCENTS.items():
            if stripped.startswith(emoji):
                flush()
                current_lines = [stripped]
                current_emoji = emoji
                current_color = accents["border"]
                matched = True
                break
        if not matched:
            current_lines.append(stripped)

    flush()
    return sections


_FONT_DISPLAY = "Georgia, 'Times New Roman', serif"
_FONT_BODY = "system-ui, -apple-system, 'Segoe UI', Arial, sans-serif"

# Brand palette
_GREEN_DEEP = "#1b4332"
_GREEN_MID = "#2d6a4f"
_TEXT_PRIMARY = "#1a1a2e"
_TEXT_SECONDARY = "#4a5568"
_TEXT_MUTED = "#718096"
_BG_WARM = "#faf9f7"
_BG_CARD = "#ffffff"
_BORDER_SUBTLE = "#e8e6e1"

# Accent colors per section — slightly muted, sophisticated variants
_SECTION_ACCENTS = {
    "🔴": {
        "bg": "#fef2f2",
        "border": "#dc2626",
        "text": "#991b1b",
    },
    "🟡": {
        "bg": "#fffbeb",
        "border": "#d97706",
        "text": "#92400e",
    },
    "🟢": {
        "bg": "#f0fdf4",
        "border": "#16a34a",
        "text": "#166534",
    },
    "💡": {
        "bg": "#eff6ff",
        "border": "#2563eb",
        "text": "#1e40af",
    },
}


def _render_section_card(emoji: str | None, color: str, content: str) -> str:
    if emoji is None:
        # Greeting / closing — elegant serif text, no card chrome
        return (
            f'<div style="padding: 28px 40px; font-family: {_FONT_DISPLAY};'
            f' font-size: 16px; line-height: 1.7; color: {_TEXT_PRIMARY};">'
            f"{content}"
            "</div>"
        )

    accents = _SECTION_ACCENTS.get(
        emoji,
        {
            "bg": _BG_CARD,
            "border": color,
            "text": color,
        },
    )
    badge_label = SECTION_BADGES.get(emoji, "")
    parts = content.split("<br>", 1)
    header_text = parts[0]
    body_text = parts[1] if len(parts) > 1 and parts[1] else ""

    body_html = ""
    if body_text:
        body_html = (
            f'<div style="padding: 0 24px 20px 24px; font-family: {_FONT_BODY};'
            f' font-size: 14px; line-height: 1.7; color: {_TEXT_SECONDARY};">'
            f"{body_text}"
            "</div>"
        )

    badge_html = (
        f'<span style="display: inline-block; background: {accents["border"]};'
        " color: #ffffff;"
        f" font-family: {_FONT_BODY};"
        " font-size: 9px; font-weight: 700; letter-spacing: 1.2px;"
        " text-transform: uppercase; padding: 3px 8px; border-radius: 3px;"
        f' margin-left: 10px; vertical-align: middle;">{badge_label}</span>'
    )

    return (
        f'<div style="margin: 0 40px 16px 40px; border-radius: 8px;'
        f' overflow: hidden; background: {accents["bg"]};">'
        # Colored top bar
        f'<div style="background: {accents["border"]}; height: 3px;"></div>'
        # Header with badge
        f'<div style="padding: 20px 24px 8px 24px; font-family: {_FONT_DISPLAY};'
        f" font-size: 17px; font-weight: 700; color: {accents['text']};"
        f' line-height: 1.3;">'
        f"{header_text}{badge_html}"
        "</div>"
        # Body text
        f"{body_html}"
        "</div>"
    )


def _wrap_html_document(body: str, month_name: str, year: int) -> str:
    month_esc = html.escape(month_name)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>"
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f"<title>Vigile by Ablo — {month_esc} {year}</title>"
        "</head>\n"
        f'<body style="margin: 0; padding: 0; background: {_BG_WARM};'
        f' font-family: {_FONT_BODY};">\n'
        # Centering wrapper
        f'<div style="background: {_BG_WARM}; padding: 40px 16px;">\n'
        # Main container
        f'<div style="max-width: 600px; margin: 0 auto; background: {_BG_CARD};'
        ' border-radius: 12px; overflow: hidden;">\n'
        # Header
        f'<div style="background: {_GREEN_DEEP};'
        f" background: linear-gradient(180deg, {_GREEN_DEEP} 0%, {_GREEN_MID} 100%);"
        ' padding: 44px 40px 40px 40px; text-align: center;">\n'
        # Vigile wordmark
        f'<p style="font-family: {_FONT_DISPLAY}; font-size: 32px;'
        " font-weight: 700; color: #ffffff; margin: 0 0 4px 0;"
        ' letter-spacing: -0.5px;">Vigile</p>\n'
        f'<p style="font-family: {_FONT_BODY}; font-size: 12px;'
        " color: #9fd4b8; color: rgba(255,255,255,0.60);"
        " margin: 0 0 20px 0; letter-spacing: 2px;"
        ' text-transform: uppercase;">by Ablo</p>\n'
        # Month/year pill
        f'<span style="display: inline-block; background: #345e4a; background: rgba(255,255,255,0.12);'
        f" font-family: {_FONT_BODY}; font-size: 11px; font-weight: 700;"
        " color: #ffffff; letter-spacing: 3px; text-transform: uppercase;"
        f' padding: 6px 20px; border-radius: 20px;">'
        f"{month_esc} {year}"
        "</span>\n"
        "</div>\n"
        # Spacer before cards
        '<div style="height: 24px;"></div>\n'
        # Section cards
        f"{body}\n"
        # Spacer after cards
        '<div style="height: 8px;"></div>\n'
        # Footer
        f'<div style="padding: 24px 40px 32px 40px; text-align: center;'
        f' border-top: 1px solid {_BORDER_SUBTLE};">'
        f'<p style="font-family: {_FONT_BODY}; font-size: 12px;'
        f' color: {_TEXT_MUTED}; margin: 0; letter-spacing: 0.5px;">'
        "Your home, looked after."
        "</p>"
        "</div>\n"
        "</div>\n"
        "</div>\n"
        "</body>\n"
        "</html>"
    )


def _build_html_from_sections(
    sections: list[tuple[str | None, str, str]], month_name: str, year: int
) -> str:
    cards = "\n".join(
        _render_section_card(emoji, color, content)
        for emoji, color, content in sections
    )
    return _wrap_html_document(cards, month_name, year)


def build_html(brief_text: str, month_name: str, year: int) -> str:
    sections = _parse_sections(brief_text)
    return _build_html_from_sections(sections, month_name, year)


def save_to_gist(
    sections: list[tuple[str | None, str, str]], month_name: str, year: int, season: str
) -> None:
    """Write the parsed brief to a GitHub Gist as JSON. Non-fatal — logs and returns on any error."""
    token = os.environ.get("GIST_TOKEN")
    gist_id = os.environ.get("GIST_ID")
    if not all([token, gist_id]):
        print("Gist secrets not configured — skipping dashboard save.")
        return
    brief_json = json.dumps(
        {
            "month": month_name,
            "year": year,
            "season": season,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sections": [
                {
                    "emoji": e,
                    "color": c,
                    "badge": SECTION_BADGES.get(e) if e else None,
                    "content": ct,
                }
                for e, c, ct in sections
            ],
        }
    )
    payload = json.dumps(
        {"files": {"vigile-brief.json": {"content": brief_json}}}
    ).encode()
    req = urllib.request.Request(
        f"https://api.github.com/gists/{gist_id}",
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
        print("Brief saved to Gist for dashboard.")
    except Exception as e:
        print(f"Gist save failed (non-fatal): {e}")


def send_email(
    plain_body: str,
    html_body: str,
    subject: str,
    sender: str,
    password: str,
    recipients: list[str],
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(plain_body, "plain"))  # fallback for plain-text clients
    msg.attach(MIMEText(html_body, "html"))  # preferred; must be last per RFC 2046
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())


def send_whatsapp(plain_body: str, month_name: str, year: int) -> None:
    """Send a WhatsApp message via Meta Cloud API. Non-fatal — logs and returns on any error."""
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    recipients_raw = os.environ.get("WHATSAPP_RECIPIENTS", "")
    if not all([token, phone_number_id, recipients_raw]):
        print("WhatsApp secrets not configured — skipping.")
        return
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
    message = (
        f"🏠 Vigile by Ablo — {month_name} {year} Home Brief\n\n{plain_body[:1000]}"
    )
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        for recipient in recipients:
            payload = json.dumps(
                {
                    "messaging_product": "whatsapp",
                    "to": recipient,
                    "type": "text",
                    "text": {"body": message},
                }
            ).encode()
            req = urllib.request.Request(
                url, data=payload, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                resp.read()
        print(f"WhatsApp sent to {len(recipients)} recipient(s).")
    except Exception as e:  # non-fatal
        print(f"WhatsApp send failed (non-fatal): {e}")


def send_telegram(plain_body: str, month_name: str, year: int) -> None:
    """Send a Telegram message via Bot API. Non-fatal — logs and returns on any error."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_ids_raw = os.environ.get("TELEGRAM_CHAT_IDS", "")
    if not all([token, chat_ids_raw]):
        print("Telegram secrets not configured — skipping.")
        return
    chat_ids = [c.strip() for c in chat_ids_raw.split(",") if c.strip()]
    message = (
        f"🏠 Vigile by Ablo — {month_name} {year} Home Brief\n\n{plain_body[:4000]}"
    )
    try:
        for chat_id in chat_ids:
            payload = json.dumps({"chat_id": chat_id, "text": message}).encode()
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                resp.read()
        print(f"Telegram sent to {len(chat_ids)} chat(s).")
    except Exception as e:  # non-fatal
        print(f"Telegram send failed (non-fatal): {e}")


def main() -> None:
    required = [
        "ANTHROPIC_API_KEY",
        "GMAIL_ADDRESS",
        "GMAIL_APP_PASSWORD",
        "RECIPIENT_EMAILS",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"Error: missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient_emails_raw = os.environ["RECIPIENT_EMAILS"]

    recipients = [e.strip() for e in recipient_emails_raw.split(",") if e.strip()]
    if not recipients:
        print("Error: RECIPIENT_EMAILS is set but contains no valid addresses")
        sys.exit(1)

    now = datetime.now(timezone.utc)
    month_name = calendar.month_name[now.month]
    year = now.year
    season = get_season(now.month)

    user_prompt = (
        f"Generate Ablo's home maintenance brief for {month_name} {year}"
        f" ({season} in South Conroe, Texas)."
    )

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        brief_text = message.content[0].text
    except anthropic.AuthenticationError as e:
        print(f"Error: Anthropic API key is invalid or missing — {e}")
        sys.exit(1)
    except anthropic.RateLimitError as e:
        print(f"Error: Anthropic API rate limit exceeded — {e}")
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {e}")
        sys.exit(1)

    subject = f"🏠 Vigile by Ablo — {month_name} {year} Home Brief"
    sections = _parse_sections(brief_text)
    html_body = _build_html_from_sections(sections, month_name, year)

    try:
        send_email(
            brief_text,
            html_body,
            subject,
            gmail_address,
            gmail_app_password,
            recipients,
        )
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error: Gmail authentication failed — check GMAIL_APP_PASSWORD — {e}")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")
        sys.exit(1)

    print(
        f"Vigile brief sent for {month_name} {year} to {len(recipients)} recipient(s)."
    )

    send_whatsapp(brief_text, month_name, year)
    send_telegram(brief_text, month_name, year)
    save_to_gist(sections, month_name, year, season)


if __name__ == "__main__":
    main()
