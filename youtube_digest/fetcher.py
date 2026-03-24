"""Fetch content from YouTube channels and websites."""

import json
import os
import re
import sys
import tempfile
from urllib.parse import urlparse


def fetch_latest_videos(channel_url: str, count: int = 3) -> list[dict]:
    import yt_dlp

    url = channel_url.strip()
    if not url.startswith("http"):
        url = f"https://www.youtube.com/{url}/videos" if url.startswith("@") \
              else f"https://www.youtube.com/@{url}/videos"
    elif "/videos" not in url:
        url = url.rstrip("/") + "/videos"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "playlist_items": f"1-{count}",
        "ignoreerrors": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = info.get("entries") or []
    videos = []
    for e in entries[:count]:
        if e:
            videos.append({
                "id": e.get("id") or e.get("url", "").split("?v=")[-1],
                "title": e.get("title", "Unknown"),
                "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
                "upload_date": e.get("upload_date", ""),
                "duration": e.get("duration"),
                "channel": info.get("uploader") or info.get("channel", ""),
                "channel_url": info.get("uploader_url") or info.get("channel_url", ""),
                "description": e.get("description", ""),
            })
    return videos


def _parse_vtt(vtt: str) -> str:
    """Extract plain text from a WebVTT subtitle file, deduplicating lines."""
    lines = []
    seen = set()
    for line in vtt.splitlines():
        line = line.strip()
        if not line or line.startswith("WEBVTT") or "-->" in line or line.startswith("NOTE"):
            continue
        text = re.sub(r"<[^>]+>", "", line).strip()
        if text and text not in seen:
            seen.add(text)
            lines.append(text)
    return " ".join(lines)


def fetch_transcript(video_id: str, cookies_file: str | None = None) -> dict:
    """Fetch transcript via yt-dlp subtitle download.

    Pass cookies_file (path to a Netscape-format cookies.txt) to authenticate
    with YouTube — required when running from cloud/VPS IPs that YouTube blocks.
    """
    import yt_dlp

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            # sb0 = storyboard/image format: no JS n-challenge needed,
            # so it works from cloud IPs even when video formats are blocked.
            "format": "sb0",
            "skip_download": True,
            "writeautomaticsub": True,
            "writesubtitles": True,
            "subtitlesformat": "vtt",
            "subtitleslangs": ["en", "de", "en-orig"],
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        if cookies_file:
            expanded = os.path.expanduser(cookies_file)
            if os.path.exists(expanded):
                ydl_opts["cookiefile"] = expanded

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception:
            pass  # subtitle file may still have been written — check below

        vtt_files = [f for f in os.listdir(tmpdir) if f.endswith(".vtt")]
        if not vtt_files:
            return {"text": "[Transcript unavailable: no subtitles found]", "language": ""}

        vtt_files.sort()  # prefer en over de
        chosen = vtt_files[0]
        lang = "en" if ".en" in chosen else chosen.split(".")[-2]

        with open(os.path.join(tmpdir, chosen), encoding="utf-8") as f:
            text = _parse_vtt(f.read())

        return {"text": text or "[Transcript empty]", "language": lang}


def fetch(channel: str, count: int = 3, cookies_file: str | None = None) -> list[dict]:
    """Full pipeline: fetch video metadata + transcripts. Returns list of video dicts."""
    print(f"Fetching latest {count} videos from {channel}...", file=sys.stderr)
    videos = fetch_latest_videos(channel, count)
    if not videos:
        raise RuntimeError("No videos found. Check the channel URL or handle.")
    for v in videos:
        print(f"  Fetching transcript: {v['title']}", file=sys.stderr)
        result = fetch_transcript(v["id"], cookies_file=cookies_file)
        v["transcript"] = result["text"]
        v["transcript_language"] = result["language"]
    return videos


def fetch_website(source: dict) -> list[dict]:
    """Fetch and extract text from up to `count` articles from a website."""
    import trafilatura

    url = source["url"]
    count = source.get("count", 10)
    source_name = source.get("name", url)
    base_domain = urlparse(url).netloc

    print(f"Fetching website: {source_name} ({url})...", file=sys.stderr)

    # Collect article URLs — try URL as direct feed first, then discover feed
    import feedparser
    from trafilatura.feeds import find_feed_urls

    article_urls = []

    # Try parsing the URL itself as an RSS/Atom feed
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        feed = feedparser.parse(downloaded)
        article_urls = [e.link for e in feed.entries if e.get("link")]

    # If not a direct feed, discover feeds on the site
    if not article_urls:
        article_urls = find_feed_urls(url)

    items = []
    for article_url in article_urls[:count * 3]:
        if len(items) >= count:
            break
        print(f"  Scraping: {article_url}", file=sys.stderr)
        try:
            downloaded = trafilatura.fetch_url(article_url)
            if not downloaded:
                continue
            text = trafilatura.extract(downloaded)
            if not text or len(text) < 200:
                continue
            metadata = trafilatura.extract_metadata(downloaded)
            items.append({
                "type": "website",
                "url": article_url,
                "title": (metadata.title if metadata and metadata.title else article_url),
                "text": text,
                "source_name": source_name,
                "publish_date": (str(metadata.date) if metadata and metadata.date else ""),
            })
        except Exception as e:
            print(f"  Warning: could not scrape {article_url}: {e}", file=sys.stderr)

    if not items:
        print(f"  Warning: no articles scraped from {source_name}", file=sys.stderr)
    return items


def fetch_all(cfg: dict) -> list[dict]:
    """Fetch all items from all configured sources. Returns a flat list."""
    sources = cfg.get("sources", [])
    cookies_file = cfg.get("cookies_file")
    all_items = []
    for source in sources:
        src_type = source.get("type", "youtube")
        try:
            if src_type == "youtube":
                items = fetch(source["url"], source.get("count", 3), cookies_file=cookies_file)
                for item in items:
                    item["source_name"] = source.get("name", source["url"])
                    item["type"] = "youtube"
                all_items.extend(items)
            elif src_type == "website":
                all_items.extend(fetch_website(source))
            else:
                print(f"Unknown source type: {src_type!r} — skipping", file=sys.stderr)
        except Exception as e:
            print(f"Error fetching {source.get('name', source['url'])}: {e}", file=sys.stderr)
    return all_items


def fetch_cmd(args) -> None:
    """Entry point for `ytdigest fetch` subcommand — prints JSON to stdout."""
    videos = fetch(args.channel, args.count)
    print(json.dumps({"videos": videos}, ensure_ascii=False, indent=2))
