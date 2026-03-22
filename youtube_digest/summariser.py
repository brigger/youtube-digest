"""Generate topic-grouped digests via `claude -p`."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DIGEST_PROMPT = """\
You are preparing a daily content digest for a busy professional.

The user is interested in these topics:
{topics_list}

Below is a JSON array of items fetched today from various sources.
Each item has a "type" (youtube or website), "title", "url", "source_name",
and either "transcript" (YouTube) or "text" (website) with the full content.

Your task:
1. Read every item.
2. For each topic, identify items that are relevant to it.
3. Write your output grouped by topic. Within each topic, write a brief summary
   of each relevant item using this format (plain text, no markdown):

TOPIC: [topic name]

  [Title] — [source_name]
  URL: [url]
  THE BIG IDEA: [one sentence capturing the most important point]
  KEY POINTS:
  - [specific detail, tool name, person, finding, or number mentioned]
  - [specific detail]
  - [specific detail]

4. If no items match a topic, write: TOPIC: [name] — nothing relevant today.
5. After all topics, add a tally:

SOURCES CHECKED
[source_name]: [N] items checked, [M] included

Rules:
- Be specific: name tools, people, companies, techniques, or statistics from the content.
- Plain text only — no asterisks, no markdown symbols.
- If a transcript is in German, summarise in English.
- Do not invent information not present in the content.
- An item can appear under multiple topics if relevant to both.

Items:
{items_json}
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
    """Send a prompt to claude -p via stdin and return the response."""
    claude_bin = _find_claude()
    cmd = [claude_bin, "-p"]
    if os.getuid() != 0:
        cmd = [claude_bin, "--dangerously-skip-permissions", "-p"]
    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed:\n{result.stderr}")
    return result.stdout.strip()


def generate(items: list[dict], topics: list[str]) -> str:
    """Generate a topic-grouped digest from fetched items."""
    for item in items:
        if item.get("type") == "youtube" and "duration" in item:
            item["duration_formatted"] = _format_duration(item.get("duration"))

    topics_list = "\n".join(f"- {t}" for t in topics) if topics else "- General interest"

    prompt = DIGEST_PROMPT.format(
        topics_list=topics_list,
        items_json=json.dumps(items, ensure_ascii=False, indent=2),
    )
    return _run_claude(prompt)
