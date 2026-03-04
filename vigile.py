#!/usr/bin/env python3
"""Vigile — automated monthly home maintenance briefing."""

import calendar
import html
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

SYSTEM_PROMPT = """\
You are Vigile, a personal home guardian for Ablo — a Senior Agile Coach based in South Conroe,
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

Produce exactly these 6 sections, in this order:

1. Warm greeting — Address Ablo by name. Reference the month, season, and one vivid climate
   detail for South Conroe. 2-3 sentences. Human and warm.

2. 🔴 Urgent — Tasks that cannot wait; risk of damage or costly consequences if skipped
   this month. Be specific about why it is urgent now.

3. 🟡 This Month — Scheduled maintenance due this month. Actionable and specific.
   Include product names (Baby Filter 2.0, Deebot, etc.) where relevant.

4. 🟢 Keep an Eye On — Items coming due in the next 4-8 weeks, or conditions to monitor.
   Helps Ablo plan ahead without overwhelming him now.

5. 💡 Blind Spot — One thing Ablo probably has not thought about this month. Pick from
   the Houston Blind Spots list if seasonally relevant. Explain briefly why it matters
   in his specific context.

6. Closing nudge — One warm, human sentence. Not corporate. Acknowledges his full plate
   and encourages action.

## Tone Rules
- Warm, human, and precise — like a knowledgeable friend who cares about Ablo's home
- Never corporate filler ("Please ensure...", "It is recommended...")
- Be specific: name the product, the chemical, the window of opportunity
- Acknowledge his context (busy professional, young family) where natural
- Never overwhelming — prioritize ruthlessly
"""

SECTION_STYLES = {
    "🔴": ("#c0392b", "#fff5f5"),
    "🟡": ("#d68910", "#fffbf0"),
    "🟢": ("#1e8449", "#f0fff4"),
    "💡": ("#2471a3", "#f0f8ff"),
}


def get_season(month: int) -> str:
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8, 9):
        return "Summer"
    if month in (10, 11):
        return "Fall"
    return "Winter"


def _parse_sections(brief_text: str) -> list[tuple[str | None, str, str, str]]:
    """Parse brief_text into sections: (emoji, border_color, bg_color, content_html)."""
    sections: list[tuple[str | None, str, str, str]] = []
    current_emoji: str | None = None
    current_color = "#444444"
    current_bg = "#f9f9f9"
    current_lines: list[str] = []

    def flush() -> None:
        if current_lines:
            content = "<br>".join(
                html.escape(ln.strip()) for ln in current_lines if ln.strip()
            )
            sections.append((current_emoji, current_color, current_bg, content))

    for line in brief_text.split("\n"):
        stripped = line.strip()
        matched = False
        for emoji, (color, bg) in SECTION_STYLES.items():
            if stripped.startswith(emoji):
                flush()
                current_lines = [stripped]
                current_emoji = emoji
                current_color = color
                current_bg = bg
                matched = True
                break
        if not matched:
            current_lines.append(stripped)

    flush()
    return sections


def _render_section_card(emoji: str | None, color: str, bg: str, content: str) -> str:
    is_header = emoji is not None
    border = f"4px solid {color}"
    card_style = (
        f"background: {bg};"
        f" border-left: {border};"
        " border-radius: 6px;"
        " padding: 16px 20px;"
        " margin: 16px 0;"
    )
    text_style = (
        "font-family: Georgia, 'Times New Roman', serif;"
        " font-size: 15px;"
        " line-height: 1.7;"
        " color: #2c2c2c;"
        " margin: 0;"
    )
    if is_header:
        # Split first line (header) from body lines
        parts = content.split("<br>", 1)
        header_html = (
            f'<p style="font-family: Georgia, serif; font-size: 17px;'
            f' font-weight: bold; color: {color}; margin: 0 0 10px 0;">'
            f"{parts[0]}</p>"
        )
        body_html = (
            f'<p style="{text_style}">{parts[1]}</p>'
            if len(parts) > 1 and parts[1]
            else ""
        )
        return f'<div style="{card_style}">{header_html}{body_html}</div>'
    return f'<div style="{card_style}"><p style="{text_style}">{content}</p></div>'


def _wrap_html_document(body: str, month_name: str, year: int) -> str:
    outer = (
        "font-family: Georgia, 'Times New Roman', serif;"
        " background: #f4f1ec;"
        " margin: 0; padding: 32px 16px;"
    )
    container = (
        "background: #ffffff;"
        " max-width: 620px;"
        " margin: 0 auto;"
        " border-radius: 10px;"
        " overflow: hidden;"
        " box-shadow: 0 2px 12px rgba(0,0,0,0.08);"
    )
    header = "background: #1a2e1a; padding: 28px 32px 24px; text-align: center;"
    logo_style = (
        "font-family: Georgia, serif;"
        " font-size: 26px;"
        " font-weight: bold;"
        " color: #e8dfc8;"
        " margin: 0 0 4px 0;"
        " letter-spacing: 1px;"
    )
    date_style = (
        "font-family: Georgia, serif;"
        " font-size: 13px;"
        " color: #8fa68f;"
        " margin: 0;"
        " letter-spacing: 2px;"
        " text-transform: uppercase;"
    )
    content_style = "padding: 24px 32px 32px;"
    footer_style = (
        "border-top: 1px solid #ede8df;"
        " padding: 16px 32px;"
        " text-align: center;"
        " font-family: Georgia, serif;"
        " font-size: 12px;"
        " color: #aaa;"
    )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>"
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f"<title>Vigile — {html.escape(month_name)} {year}</title>"
        "</head>\n"
        f'<body style="{outer}">\n'
        f'  <div style="{container}">\n'
        f'    <div style="{header}">\n'
        f'      <p style="{logo_style}">🏠 Vigile</p>\n'
        f'      <p style="{date_style}">{html.escape(month_name)} {year}</p>\n'
        "    </div>\n"
        f'    <div style="{content_style}">\n'
        f"{body}\n"
        "    </div>\n"
        f'    <div style="{footer_style}">Your home, looked after.</div>\n'
        "  </div>\n"
        "</body>\n"
        "</html>"
    )


def build_html(brief_text: str, month_name: str, year: int) -> str:
    sections = _parse_sections(brief_text)
    cards = "\n".join(
        _render_section_card(emoji, color, bg, content)
        for emoji, color, bg, content in sections
    )
    return _wrap_html_document(cards, month_name, year)


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
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())


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
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
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

    subject = f"🏠 Vigile — {month_name} {year} Home Brief"
    html_body = build_html(brief_text, month_name, year)

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
    sys.exit(0)


if __name__ == "__main__":
    main()
