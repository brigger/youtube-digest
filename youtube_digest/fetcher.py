"""Fetch latest N videos and transcripts from a YouTube channel."""

import json
import sys


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


def fetch_transcript(video_id: str) -> dict:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

    api = YouTubeTranscriptApi()
    try:
        transcript_list = api.list(video_id)
        try:
            t = transcript_list.find_manually_created_transcript(["en"])
        except NoTranscriptFound:
            try:
                t = transcript_list.find_generated_transcript(["en"])
            except NoTranscriptFound:
                t = next(iter(transcript_list))
        data = t.fetch()
        text = " ".join(s.text for s in data)
        return {"text": text, "language": t.language}
    except TranscriptsDisabled:
        return {"text": "[Transcript unavailable: subtitles disabled]", "language": ""}
    except StopIteration:
        return {"text": "[Transcript unavailable: no transcripts found]", "language": ""}
    except Exception as e:
        return {"text": f"[Error fetching transcript: {e}]", "language": ""}


def fetch(channel: str, count: int = 3) -> list[dict]:
    """Full pipeline: fetch video metadata + transcripts. Returns list of video dicts."""
    print(f"Fetching latest {count} videos from {channel}...", file=sys.stderr)
    videos = fetch_latest_videos(channel, count)
    if not videos:
        raise RuntimeError("No videos found. Check the channel URL or handle.")
    for v in videos:
        print(f"  Fetching transcript: {v['title']}", file=sys.stderr)
        result = fetch_transcript(v["id"])
        v["transcript"] = result["text"]
        v["transcript_language"] = result["language"]
    return videos


def fetch_cmd(args) -> None:
    """Entry point for `ytdigest fetch` subcommand — prints JSON to stdout."""
    videos = fetch(args.channel, args.count)
    print(json.dumps({"videos": videos}, ensure_ascii=False, indent=2))
