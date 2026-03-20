# YouTube Daily Digest — Setup Info

## VPS Server (DiscoFox)

| Field       | Value               |
|-------------|---------------------|
| IP          | 95.217.222.205      |
| User        | root                |
| Auth        | SSH key (~/.ssh/id_ed25519) |
| Hostname    | DiscoFox            |
| OS          | Ubuntu 24.04.3 LTS  |

SSH: `ssh root@95.217.222.205`

## Gmail

| Field         | Value                  |
|---------------|------------------------|
| Account       | ddiscofox@gmail.com    |
| App password  | fwzj jxwq fhjq wrez    |
| Recipients    | ddiscofox@gmail.com, patrick@getabstract.com |

## Cron Jobs

**VPS** — 6:00am UTC (7:00am Swiss time):
```
0 6 * * * python3 /root/youtube-digest/scripts/youtube-daily-digest.py >> /root/youtube-digest/digest.log 2>&1
```

**Mac** — 6:00am local time:
```
0 6 * * * /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Users/patrick/Documents/youtube-digest/youtube-daily-digest.py >> /Users/patrick/Documents/youtube-digest/digest.log 2>&1
```

## Files

| Location | Description |
|----------|-------------|
| `~/Documents/youtube-digest/youtube-daily-digest.py` | Main digest script (Mac) |
| `~/Documents/youtube-digest/fetch_channel.py` | YouTube fetcher (Mac) |
| `~/Documents/youtube-digest/digest.log` | Cron log (Mac) |
| `/root/youtube-digest/youtube-daily-digest.py` | Main digest script (VPS) |
| `/root/youtube-digest/fetch_channel.py` | YouTube fetcher (VPS) |
| `/root/youtube-digest/digest.log` | Cron log (VPS) |

## Claude Code Skill

The interactive Claude skill (used when asking Claude directly to summarise a channel) lives separately in the plugin directory:

| Location | Description |
|----------|-------------|
| `~/.claude/local-plugins/plugins/youtube-channel-summary/skills/youtube-channel-summary/SKILL.md` | Skill definition |
| `~/Documents/youtube-digest/fetch_channel.py` | Fetcher used by both the skill and the cron digest |
