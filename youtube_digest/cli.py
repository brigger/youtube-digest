"""ytdigest — command-line interface."""

import argparse
import sys
from pathlib import Path


# ── Subcommand handlers ────────────────────────────────────────────────────────

def cmd_run(args) -> None:
    from . import config as cfg_mod, fetcher, summariser, emailer

    cfg = cfg_mod.load(Path(args.config) if args.config else None)

    if not cfg.get("sources"):
        sys.exit("No sources configured. Run `ytdigest init` or `ytdigest sources add <url>`.")

    items = fetcher.fetch_all(cfg)
    topics = cfg.get("topics", [])
    summary = summariser.generate(items, topics)

    if args.no_email:
        print(summary)
    else:
        emailer.send(summary, cfg)


def cmd_init(_args) -> None:
    from . import config as cfg_mod

    print("ytdigest setup wizard\n" + "=" * 40)

    channel = input("YouTube channel URL or @handle [@madymorrison]: ").strip()
    if not channel:
        channel = "https://www.youtube.com/@madymorrison"
    name = input(f"Display name for this source [{channel}]: ").strip() or channel

    count_raw = input("Number of videos to fetch [3]: ").strip()
    count = int(count_raw) if count_raw.isdigit() else 3

    print("\nTopics to filter by (one per line, blank line to finish):")
    topics = []
    while True:
        t = input("  Topic: ").strip()
        if not t:
            break
        topics.append(t)
    if not topics:
        topics = ["General interest"]

    from_addr = input("\nSend FROM email address: ").strip()
    to_raw = input("Send TO (comma-separated): ").strip()
    to_addrs = [a.strip() for a in to_raw.split(",") if a.strip()]

    print("\nSMTP settings (Gmail defaults shown):")
    smtp_host = input("SMTP host [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    port_raw = input("SMTP port — 465 (SSL) or 587 (STARTTLS) [465]: ").strip()
    smtp_port = int(port_raw) if port_raw.isdigit() else 465
    smtp_user = input(f"SMTP user [{from_addr}]: ").strip() or from_addr

    print("\nPassword — store as env var name (recommended) or inline:")
    pass_env = input("  Env var name [GMAIL_PASSWORD]: ").strip() or "GMAIL_PASSWORD"

    cfg = {
        "topics": topics,
        "sources": [
            {"url": channel, "type": "youtube", "name": name, "count": count}
        ],
        "email": {
            "from": from_addr,
            "to": to_addrs,
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_user": smtp_user,
            "smtp_pass_env": pass_env,
        },
    }
    cfg_mod.save(cfg)
    print("\nDone. Run `ytdigest run` to test it.")


def cmd_test_email(args) -> None:
    from . import config as cfg_mod, emailer

    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    emailer.send(
        "This is a test email from ytdigest. If you received it, your config is working.",
        cfg,
        subject="ytdigest — test email",
    )
    print("Test email sent.")


def cmd_fetch(args) -> None:
    from .fetcher import fetch_cmd
    fetch_cmd(args)


def cmd_listen(args) -> None:
    from . import config as cfg_mod
    from .listener import listen

    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    listen(cfg, interval=args.interval)


# ── Sources subcommands ────────────────────────────────────────────────────────

def cmd_sources_list(args) -> None:
    from . import config as cfg_mod
    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    sources = cfg.get("sources", [])
    if not sources:
        print("No sources configured.")
        return
    for i, s in enumerate(sources):
        print(f"[{i}] {s.get('name', s['url'])}  type={s.get('type', 'youtube')}  count={s.get('count', 3)}")
        print(f"     {s['url']}")


def cmd_sources_add(args) -> None:
    from . import config as cfg_mod
    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    cfg.setdefault("sources", []).append({
        "url": args.url,
        "type": args.type,
        "name": args.name or args.url,
        "count": args.count,
    })
    cfg_mod.save(cfg)
    print(f"Added source: {args.url}")


def cmd_sources_remove(args) -> None:
    from . import config as cfg_mod
    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    sources = cfg.get("sources", [])
    before = len(sources)
    cfg["sources"] = [s for s in sources if s["url"] != args.url]
    if len(cfg["sources"]) == before:
        sys.exit(f"No source found with URL: {args.url}")
    cfg_mod.save(cfg)
    print(f"Removed source: {args.url}")


# ── Topics subcommands ─────────────────────────────────────────────────────────

def cmd_topics_list(args) -> None:
    from . import config as cfg_mod
    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    topics = cfg.get("topics", [])
    if not topics:
        print("No topics configured.")
        return
    for i, t in enumerate(topics):
        print(f"[{i}] {t}")


def cmd_topics_add(args) -> None:
    from . import config as cfg_mod
    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    cfg.setdefault("topics", []).append(args.text)
    cfg_mod.save(cfg)
    print(f"Added topic: {args.text}")


def cmd_topics_remove(args) -> None:
    from . import config as cfg_mod
    cfg = cfg_mod.load(Path(args.config) if args.config else None)
    topics = cfg.get("topics", [])
    idx = args.index
    if idx < 0 or idx >= len(topics):
        sys.exit(f"Invalid index: {idx}. Use `ytdigest topics list` to see indices.")
    removed = topics.pop(idx)
    cfg_mod.save(cfg)
    print(f"Removed topic [{idx}]: {removed}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ytdigest",
        description="Daily digest — fetch YouTube & websites, filter by topic, email the result.",
    )
    parser.add_argument("--config", metavar="PATH", help="Config file (default: ~/.config/ytdigest/config.yaml)")

    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # run
    run_p = sub.add_parser("run", help="Run the full digest pipeline once")
    run_p.add_argument("--no-email", action="store_true", help="Print summary instead of emailing")

    # init
    sub.add_parser("init", help="Interactive setup wizard")

    # test-email
    sub.add_parser("test-email", help="Send a test email to verify SMTP config")

    # fetch (used by the Claude Code skill)
    fetch_p = sub.add_parser("fetch", help="Fetch videos + transcripts and print JSON")
    fetch_p.add_argument("channel", help="Channel URL, @handle, or name")
    fetch_p.add_argument("--count", type=int, default=3, help="Number of videos (default 3)")

    # listen
    listen_p = sub.add_parser("listen", help="Poll inbox every N seconds and reply to instructions")
    listen_p.add_argument("--interval", type=int, default=30, help="Poll interval in seconds (default 30)")

    # sources
    sources_p = sub.add_parser("sources", help="Manage content sources")
    sources_sub = sources_p.add_subparsers(dest="sources_command", metavar="action")
    sources_sub.required = True

    sources_sub.add_parser("list", help="List all sources")

    sa = sources_sub.add_parser("add", help="Add a source")
    sa.add_argument("url", help="Source URL")
    sa.add_argument("--type", choices=["youtube", "website"], default="youtube", help="Source type (default: youtube)")
    sa.add_argument("--name", help="Display name")
    sa.add_argument("--count", type=int, default=3, help="Number of items to fetch")

    sr = sources_sub.add_parser("remove", help="Remove a source by URL")
    sr.add_argument("url", help="Source URL to remove")

    # topics
    topics_p = sub.add_parser("topics", help="Manage digest topics")
    topics_sub = topics_p.add_subparsers(dest="topics_command", metavar="action")
    topics_sub.required = True

    topics_sub.add_parser("list", help="List all topics")

    ta = topics_sub.add_parser("add", help="Add a topic")
    ta.add_argument("text", help="Topic description")

    tr = topics_sub.add_parser("remove", help="Remove a topic by index")
    tr.add_argument("index", type=int, help="Topic index (from `topics list`)")

    args = parser.parse_args()

    if args.command == "sources":
        dispatch = {
            "list": cmd_sources_list,
            "add": cmd_sources_add,
            "remove": cmd_sources_remove,
        }
        dispatch[args.sources_command](args)
    elif args.command == "topics":
        dispatch = {
            "list": cmd_topics_list,
            "add": cmd_topics_add,
            "remove": cmd_topics_remove,
        }
        dispatch[args.topics_command](args)
    else:
        dispatch = {
            "run": cmd_run,
            "init": cmd_init,
            "test-email": cmd_test_email,
            "fetch": cmd_fetch,
            "listen": cmd_listen,
        }
        dispatch[args.command](args)


if __name__ == "__main__":
    main()
