#!/usr/bin/env python3
"""Vigile — automated monthly home maintenance briefing."""

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

SECTION_COLORS = {
    "🔴": "#c0392b",
    "🟡": "#d68910",
    "🟢": "#1e8449",
    "💡": "#2471a3",
}

MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def get_season(month: int) -> str:
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8, 9):
        return "Summer"
    if month in (10, 11):
        return "Fall"
    return "Winter"


def build_html(brief_text: str) -> str:
    lines = brief_text.split("\n")
    html_parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_parts.append("<br>")
            continue
        section_color = None
        for emoji, color in SECTION_COLORS.items():
            if stripped.startswith(emoji):
                section_color = color
                break
        escaped = html.escape(stripped)
        if section_color:
            style = (
                f"font-size: 18px; font-weight: bold; color: {section_color};"
                " margin: 24px 0 8px 0;"
            )
            html_parts.append(f'<p style="{style}">{escaped}</p>')
        else:
            html_parts.append(f'<p style="margin: 4px 0;">{escaped}</p>')
    body_html = "\n".join(html_parts)
    container_style = (
        "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;"
        " max-width: 640px; margin: 0 auto; padding: 24px;"
        " line-height: 1.6; color: #1a1a1a; background: #ffffff;"
    )
    return (
        "<!DOCTYPE html>\n"
        "<html>\n"
        f'<body style="{container_style}">\n'
        f"{body_html}\n"
        "</body>\n"
        "</html>"
    )


def send_email(
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
    msg.attach(MIMEText(html_body, "html"))
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

    api_key = os.environ["ANTHROPIC_API_KEY"]
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient_emails_raw = os.environ["RECIPIENT_EMAILS"]

    recipients = [e.strip() for e in recipient_emails_raw.split(",") if e.strip()]
    if not recipients:
        print("Error: RECIPIENT_EMAILS is set but contains no valid addresses")
        sys.exit(1)

    now = datetime.now(timezone.utc)
    month_name = MONTH_NAMES[now.month - 1]
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
    except Exception as e:
        print(f"Error calling Anthropic API: {e}")
        sys.exit(1)

    subject = f"🏠 Vigile — {month_name} {year} Home Brief"
    html_body = build_html(brief_text)

    try:
        send_email(html_body, subject, gmail_address, gmail_app_password, recipients)
    except Exception as e:
        print(f"Error sending email: {e}")
        sys.exit(1)

    print(f"Vigile brief sent for {month_name} {year} to {len(recipients)} recipient(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
