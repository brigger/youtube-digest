# YouTube Daily Digest

Daily email digest of the latest YouTube videos from a channel, summarised by Claude.
GitHub: https://github.com/brigger/youtube-digest

## Install

```bash
pip install git+https://github.com/brigger/youtube-digest
```

## Commands

```bash
ytdigest run          # fetch, summarise, email
ytdigest init         # interactive setup wizard
ytdigest test-email   # verify SMTP config
ytdigest fetch @mkbhd # fetch & print JSON (for debugging)
```

## Config

Lives at `~/.config/ytdigest/config.yaml`. See `config.example.yaml` for all options.

## VPS Server (DiscoFox)

| Field    | Value                       |
|----------|-----------------------------|
| IP       | 95.217.222.205              |
| User     | root                        |
| Auth     | SSH key (~/.ssh/id_ed25519) |
| OS       | Ubuntu 24.04.3 LTS          |

SSH: `ssh root@95.217.222.205`

### Cron (6:00am UTC = 7:00am Swiss time)

```
0 6 * * * /usr/local/bin/ytdigest run >> /root/youtube-digest/digest.log 2>&1
```

### Config on VPS

`~/.config/ytdigest/config.yaml` — channel, email, cookies_file.

## Gmail

| Field        | Value                                        |
|--------------|----------------------------------------------|
| Account      | ddiscofox@gmail.com                          |
| App password | fwzj jxwq fhjq wrez                          |
| Recipients   | ddiscofox@gmail.com, patrick@getabstract.com |

## YouTube Cookies (VPS)

The VPS IP is a cloud IP — YouTube requires authenticated cookies to allow subtitle downloads.
Cookies are stored at `~/.config/ytdigest/youtube-cookies.txt` on the VPS.

When transcripts stop working, re-export from Mac (must be logged into YouTube in Chrome):

```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/yt-dlp \
  --cookies-from-browser chrome \
  --cookies /tmp/youtube-cookies.txt \
  --skip-download --quiet "https://www.youtube.com/"

scp /tmp/youtube-cookies.txt root@95.217.222.205:~/.config/ytdigest/youtube-cookies.txt
```

## Claude Code Skill

Interactive skill for summarising any channel on demand:

| Location | Description |
|----------|-------------|
| `~/.claude/local-plugins/plugins/youtube-channel-summary/skills/youtube-channel-summary/SKILL.md` | Skill definition |
