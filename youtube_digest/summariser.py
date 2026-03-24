"""Generate topic-grouped digests via `claude -p`."""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_TOPIC_PROMPT_FILE = Path(__file__).parent / "prompt_topic.md"
_EMAIL_SHELL_FILE = Path(__file__).parent / "email_shell.md"
TOPIC_PROMPT = _TOPIC_PROMPT_FILE.read_text(encoding="utf-8")
EMAIL_SHELL = _EMAIL_SHELL_FILE.read_text(encoding="utf-8")

# Keep loading the old prompt for the reply feature
_REPLY_PROMPT_FALLBACK = Path(__file__).parent / "prompt.md"


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
    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=600, cwd=Path.home())
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed:\n{result.stderr}")
    return result.stdout.strip()


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _parse_topic(t) -> dict:
    if isinstance(t, str):
        return {"name": t, "count": 5}
    return {"name": t.get("name", ""), "count": int(t.get("count", 5))}


def _generate_topic(items_json: str, topic_name: str, topic_count: int, topic_slug: str) -> tuple[str, str, str]:
    """Call Claude for one topic. Returns (toc_li_html, section_html, markdown)."""
    print(f"  Generating topic: {topic_name}...", file=sys.stderr)
    prompt = TOPIC_PROMPT.format(
        topic_name=topic_name,
        topic_slug=topic_slug,
        topic_count=topic_count,
        items_json=items_json,
    )
    response = _run_claude(prompt)
    if "===TOC===" in response and "===SECTION===" in response:
        _, rest = response.split("===TOC===", 1)
        if "===MARKDOWN===" in rest:
            middle, md = rest.split("===MARKDOWN===", 1)
        else:
            middle, md = rest, ""
        toc_li, section = middle.split("===SECTION===", 1)
        return toc_li.strip(), section.strip(), md.strip()
    # Fallback
    toc_li = f'<li><a href="#topic-{topic_slug}">{topic_name}</a></li>'
    return toc_li, response, f"## {topic_name}\n\n{response}"


def generate(items: list[dict], topics: list) -> str:
    """Generate a topic-grouped digest, calling Claude once per topic."""
    _MAX_TEXT_CHARS = 3000
    for item in items:
        if item.get("type") == "youtube" and "duration" in item:
            item["duration_formatted"] = _format_duration(item.get("duration"))
        for field in ("text", "transcript"):
            if field in item and len(item[field]) > _MAX_TEXT_CHARS:
                item[field] = item[field][:_MAX_TEXT_CHARS] + "…"

    items_json = json.dumps(items, ensure_ascii=False, indent=2)
    parsed = [_parse_topic(t) for t in topics] if topics else [{"name": "General interest", "count": 5}]

    toc_parts = []
    section_parts = []
    md_parts = []
    for t in parsed:
        slug = _slug(t["name"])
        toc_li, section, md = _generate_topic(items_json, t["name"], t["count"], slug)
        toc_parts.append(toc_li)
        section_parts.append(section)
        md_parts.append(md)

    # Build sources summary
    source_counts: dict[str, int] = {}
    for item in items:
        name = item.get("source_name", "Unknown")
        source_counts[name] = source_counts.get(name, 0) + 1
    sources_html = "\n".join(
        f'          <li><strong>{name}:</strong> {n} items</li>'
        for name, n in source_counts.items()
    )

    date_str = datetime.now().strftime("%A, %B %-d, %Y")
    toc_items = "\n".join(f"          {li}" for li in toc_parts)
    sections = '\n      <hr class="divider"/>\n'.join(section_parts)

    html = EMAIL_SHELL.format(
        date=date_str,
        toc_items=toc_items,
        sections=sections,
        sources_html=sources_html,
        total_n=len(items),
    )

    source_names = ", ".join(source_counts.keys())
    markdown = f"# Daily Content Digest — {date_str}\n\n_Sources: {source_names}_\n\n---\n\n" + \
               "\n\n---\n\n".join(md_parts)

    return {"html": html, "markdown": markdown}
