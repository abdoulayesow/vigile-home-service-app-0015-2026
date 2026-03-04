# Email Utility Patterns

Project-grounded examples for Gmail SMTP and HTML email construction in Vigile.

## SMTP Send Pattern: Context Manager + STARTTLS

Always use a context manager for the SMTP connection. Always call `starttls()` before `login()`:

```python
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
        smtp.starttls()               # Must come before login
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())
```

Key elements:
- `MIMEMultipart("alternative")` — signals the email has an HTML version
- `msg["To"]` — display header (comma-joined for readability)
- `smtp.sendmail(sender, recipients, ...)` — actual delivery; `recipients` is a `list[str]`
- `smtp.starttls()` before `smtp.login()` — required for Gmail App Password auth

## HTML Email Construction

Convert plain text to HTML line by line. Escape all content before embedding:

```python
def build_html(brief_text: str) -> str:
    lines = brief_text.split("\n")
    html_parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_parts.append("<br>")
            continue
        escaped = html.escape(stripped)      # Always escape
        html_parts.append(f'<p style="margin: 4px 0;">{escaped}</p>')
    body_html = "\n".join(html_parts)
    return f"<!DOCTYPE html>\n<html>\n<body>\n{body_html}\n</body>\n</html>"
```

Always call `html.escape()` — even on AI-generated text — to prevent malformed HTML.

## Styling Section Headers

Detect emoji section markers and apply bold colored styles:

```python
SECTION_COLORS = {
    "🔴": "#c0392b",
    "🟡": "#d68910",
    "🟢": "#1e8449",
    "💡": "#2471a3",
}

for emoji, color in SECTION_COLORS.items():
    if stripped.startswith(emoji):
        section_color = color
        break

if section_color:
    style = f"font-size: 18px; font-weight: bold; color: {section_color}; margin: 24px 0 8px 0;"
    html_parts.append(f'<p style="{style}">{escaped}</p>')
```

## Multi-Recipient Delivery

Split `RECIPIENT_EMAILS` on commas and strip whitespace:

```python
recipients = [e.strip() for e in recipient_emails_raw.split(",") if e.strip()]
```

`sendmail` accepts a list of addresses for delivery. The `msg["To"]` header shows them joined.

## Error Handling

Wrap the entire send operation:

```python
try:
    send_email(html_body, subject, gmail_address, gmail_app_password, recipients)
except Exception as e:
    print(f"Error sending email: {e}")
    sys.exit(1)
```

Never print `gmail_app_password` in error messages — even accidentally via `{e}`.
