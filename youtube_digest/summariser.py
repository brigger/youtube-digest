"""Generate topic-grouped digests via `claude -p`."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

_PROMPT_FILE = Path(__file__).parent / "prompt.md"
DIGEST_PROMPT = _PROMPT_FILE.read_text(encoding="utf-8")


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


def _parse_topic(t) -> dict:
    if isinstance(t, str):
        return {"name": t, "count": 5}
    return {"name": t.get("name", ""), "count": int(t.get("count", 5))}


def generate(items: list[dict], topics: list) -> str:
    """Generate a topic-grouped digest from fetched items."""
    for item in items:
        if item.get("type") == "youtube" and "duration" in item:
            item["duration_formatted"] = _format_duration(item.get("duration"))

    parsed = [_parse_topic(t) for t in topics] if topics else [{"name": "General interest", "count": 5}]
    topics_list = "\n".join(f"- {t['name']} (max {t['count']} items)" for t in parsed)

    prompt = DIGEST_PROMPT.format(
        topics_list=topics_list,
        items_json=json.dumps(items, ensure_ascii=False, indent=2),
    )
    return _run_claude(prompt)
