"""Send the digest email via SMTP."""

import os
import smtplib
import ssl
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import certifi


def _get_password(email_cfg: dict) -> str:
    if "smtp_pass_env" in email_cfg:
        pwd = os.environ.get(email_cfg["smtp_pass_env"])
        if not pwd:
            sys.exit(
                f"Environment variable {email_cfg['smtp_pass_env']} is not set.\n"
                "Export it before running: export GMAIL_PASSWORD=your-app-password"
            )
        return pwd
    if "smtp_pass" in email_cfg:
        return email_cfg["smtp_pass"]
    sys.exit("No password configured. Set smtp_pass_env or smtp_pass in config.yaml.")


def send(body: str, cfg: dict, subject: str | None = None, attachments: list[tuple[str, str]] | None = None) -> None:
    email_cfg = cfg["email"]
    from_addr = email_cfg["from"]
    to_addrs = email_cfg["to"]
    smtp_host = email_cfg.get("smtp_host", "smtp.gmail.com")
    smtp_port = email_cfg.get("smtp_port", 587)
    smtp_user = email_cfg.get("smtp_user", from_addr)
    password = _get_password(email_cfg)

    today = date.today().strftime("%B %d, %Y")
    subject = subject or f"Daily Digest — {today}"

    msg = MIMEMultipart("alternative")
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject

    is_html = body.lstrip().startswith("<!DOCTYPE") or body.lstrip().startswith("<html")
    if is_html:
        msg.attach(MIMEText(body, "html", "utf-8"))
    else:
        msg.attach(MIMEText(body, "plain", "utf-8"))

    for filename, content in (attachments or []):
        part = MIMEText(content, "plain", "utf-8")
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)

    ctx = ssl.create_default_context(cafile=certifi.where())

    print(f"Sending email to {to_addrs}...", file=sys.stderr)
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx, timeout=30) as s:
            s.login(smtp_user, password)
            s.sendmail(from_addr, to_addrs, msg.as_string())
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.login(smtp_user, password)
            s.sendmail(from_addr, to_addrs, msg.as_string())
    print("Email sent.", file=sys.stderr)
