"""Poll Gmail IMAP for reply emails and respond via claude -p."""

import email
import email.header
import imaplib
import json
import os
import re
import ssl
import sys
import time
from pathlib import Path

import certifi

from . import emailer, fetcher, summariser

PROCESSED_IDS_FILE = Path.home() / ".config" / "ytdigest" / "processed_ids.txt"

REPLY_PROMPT = """\
You are managing a YouTube digest email service for a busy professional.

The user replied to their daily digest email with this message:
---
{instruction}
---

Here are the latest {n} videos from {channel} with full transcripts.

Respond to the user's message. Depending on what they asked:
- If they want more summaries, provide them in the same GetAbstract format (plain text, no markdown).
- If they asked a question about the content, answer it specifically using the transcripts.
- If they mentioned a different channel, note that you are working with the configured channel for now.
- If it's a general comment or feedback, acknowledge it warmly and briefly.

Keep your response focused and practical. Plain text only — no asterisks, no markdown symbols.

Video data:
{video_json}
"""


def _load_processed() -> set:
    if PROCESSED_IDS_FILE.exists():
        return set(PROCESSED_IDS_FILE.read_text().splitlines())
    return set()


def _save_processed(ids: set) -> None:
    PROCESSED_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_IDS_FILE.write_text("\n".join(sorted(ids)))


def _decode_header(value: str) -> str:
    parts = email.header.decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _get_body(msg) -> str:
    """Extract plain text body, stripping quoted reply text."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
    else:
        charset = msg.get_content_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")

    # Strip quoted reply lines (lines starting with ">") and common footers
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            break  # everything after the first quote block is old content
        lines.append(line)

    return "\n".join(lines).strip()


def check_inbox(cfg: dict) -> list[tuple]:
    """Return list of (uid, from_addr, subject, body) for unread emails."""
    email_cfg = cfg["email"]
    user = email_cfg.get("smtp_user", email_cfg["from"])
    password = emailer._get_password(email_cfg)
    imap_host = email_cfg.get("imap_host", "imap.gmail.com")

    ctx = ssl.create_default_context(cafile=certifi.where())
    with imaplib.IMAP4_SSL(imap_host, 993, ssl_context=ctx) as imap:
        imap.login(user, password)
        imap.select("INBOX")

        _, data = imap.search(None, "UNSEEN")
        uids = data[0].split()
        if not uids:
            return []

        results = []
        for uid in uids:
            _, msg_data = imap.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            from_addr = _decode_header(msg.get("From", ""))
            subject = _decode_header(msg.get("Subject", ""))
            body = _get_body(msg)

            # Only process replies to our digest emails
            is_reply = subject.lower().startswith("re:")
            is_digest = "youtube digest" in subject.lower() or "mady morrison" in subject.lower()
            has_reply_to = msg.get("In-Reply-To") is not None

            if not body or not (is_reply and (is_digest or has_reply_to)):
                continue

            results.append((uid.decode(), from_addr, subject, body))

        return results


def process_reply(body: str, cfg: dict) -> str:
    """Fetch videos and generate a reply using claude -p."""
    channel = cfg.get("channel", "https://www.youtube.com/@madymorrison")
    count = cfg.get("count", 3)
    cookies_file = cfg.get("cookies_file")

    print(f"  Fetching {count} videos to generate reply...", file=sys.stderr)
    videos = fetcher.fetch(channel, count, cookies_file=cookies_file)

    for v in videos:
        v["duration_formatted"] = summariser._format_duration(v.get("duration"))

    channel_name = videos[0].get("channel", channel) if videos else channel

    prompt = REPLY_PROMPT.format(
        instruction=body,
        n=len(videos),
        channel=channel_name,
        video_json=json.dumps(videos, ensure_ascii=False, indent=2),
    )

    return summariser._run_claude(prompt)


def listen(cfg: dict, interval: int = 30) -> None:
    processed = _load_processed()
    print(f"Listening for email replies every {interval}s... (Ctrl+C to stop)", file=sys.stderr)

    while True:
        try:
            messages = check_inbox(cfg)
            for uid, from_addr, subject, body in messages:
                if uid in processed:
                    continue

                print(f"New email from {from_addr}: {subject!r}", file=sys.stderr)
                print(f"  Instruction: {body[:100]}...", file=sys.stderr)

                response = process_reply(body, cfg)

                reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
                emailer.send(response, cfg, subject=reply_subject)

                processed.add(uid)
                _save_processed(processed)
                print("  Reply sent.", file=sys.stderr)

        except KeyboardInterrupt:
            print("\nStopped.", file=sys.stderr)
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

        time.sleep(interval)
