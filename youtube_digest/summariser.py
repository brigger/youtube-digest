"""Generate GetAbstract-style summaries via `claude -p`."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SUMMARY_PROMPT = """\
You are writing GetAbstract-style video briefs for a busy professional.

Below is JSON for {n} YouTube videos from {channel}.
For each video produce this exact structure (plain text, no markdown):

---
VIDEO {num}: [Title] ([M:SS duration])
URL: [url]

THE BIG IDEA
One sentence capturing the single most important point.

KEY TAKEAWAYS
1. [specific, actionable takeaway]
2. [specific, actionable takeaway]
3. [specific, actionable takeaway]
4. [specific, actionable takeaway]
5. [specific, actionable takeaway]

SUMMARY
[Section heading]: 2-3 sentences on the main theme.
[Section heading]: 2-3 sentences on a secondary theme.
[Section heading]: 2-3 sentences on implications or closing thought.

BOTTOM LINE
1-2 sentences: who should care and why it matters.
---

After all briefs add:

CHANNEL PULSE — {channel}
[1-2 sentences on recurring themes across these videos]
[1 sentence on audience fit]

Rules:
- Be specific: name poses, techniques, durations, products, or people mentioned.
- If transcript is in German, summarise in English.
- If transcript is unavailable, work from the title and description only.
- Plain text only — no asterisks, no markdown symbols.

Video data:
{video_json}
"""


def _find_claude() -> str:
    claude = shutil.which("claude")
    if claude:
        return claude
    for p in [Path.home() / ".local/bin/claude", Path("/usr/local/bin/claude")]:
        if p.exists():
            return str(p)
    sys.exit("claude CLI not found. Install it from https://claude.ai/download")


def _format_duration(seconds: float | None) -> str:
    if not seconds:
        return "?"
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def _run_claude(prompt: str) -> str:
    """Send a prompt to claude -p and return the response."""
    claude_bin = _find_claude()
    cmd = [claude_bin, "-p", prompt]
    if os.getuid() != 0:
        cmd = [claude_bin, "--dangerously-skip-permissions", "-p", prompt]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed:\n{result.stderr}")
    return result.stdout.strip()


def generate(videos: list[dict]) -> str:
    for v in videos:
        v["duration_formatted"] = _format_duration(v.get("duration"))

    channel_name = videos[0].get("channel", "the channel") if videos else "the channel"

    prompt = SUMMARY_PROMPT.format(
        n=len(videos),
        channel=channel_name,
        num="{num}",
        video_json=json.dumps(videos, ensure_ascii=False, indent=2),
    )

    return _run_claude(prompt)
