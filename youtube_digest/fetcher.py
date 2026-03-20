"""Fetch latest N videos and transcripts from a YouTube channel."""

import json
import os
import re
import sys
import tempfile


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


def fetch_cmd(args) -> None:
    """Entry point for `ytdigest fetch` subcommand — prints JSON to stdout."""
    videos = fetch(args.channel, args.count)
    print(json.dumps({"videos": videos}, ensure_ascii=False, indent=2))
