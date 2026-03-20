"""ytdigest — command-line interface."""

import argparse
import sys
from pathlib import Path


# ── Subcommand handlers ────────────────────────────────────────────────────────

def cmd_run(args) -> None:
    from . import config as cfg_mod, fetcher, summariser, emailer

    cfg = cfg_mod.load(Path(args.config) if args.config else None)

    channel = args.channel or cfg.get("channel")
    count = args.count or cfg.get("count", 3)

    if not channel:
        sys.exit("No channel specified. Set it in config.yaml or pass --channel.")

    cookies_file = cfg.get("cookies_file")
    videos = fetcher.fetch(channel, count, cookies_file=cookies_file)
    summary = summariser.generate(videos)

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

    count_raw = input("Number of videos to summarise [3]: ").strip()
    count = int(count_raw) if count_raw.isdigit() else 3

    from_addr = input("Send FROM email address: ").strip()
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
        "channel": channel,
        "count": count,
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


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ytdigest",
        description="YouTube channel digest — fetch, summarise with Claude, email.",
    )
    parser.add_argument("--config", metavar="PATH", help="Config file (default: ~/.config/ytdigest/config.yaml)")

    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # run
    run_p = sub.add_parser("run", help="Run the full digest pipeline once")
    run_p.add_argument("--channel", help="Override channel from config")
    run_p.add_argument("--count", type=int, help="Override video count from config")
    run_p.add_argument("--no-email", action="store_true", help="Print summary instead of emailing")

    # init
    sub.add_parser("init", help="Interactive setup wizard")

    # test-email
    sub.add_parser("test-email", help="Send a test email to verify SMTP config")

    # fetch  (used by the Claude Code skill)
    fetch_p = sub.add_parser("fetch", help="Fetch videos + transcripts and print JSON")
    fetch_p.add_argument("channel", help="Channel URL, @handle, or name")
    fetch_p.add_argument("--count", type=int, default=3, help="Number of videos (default 3)")

    # listen
    listen_p = sub.add_parser("listen", help="Poll inbox every N seconds and reply to instructions")
    listen_p.add_argument("--interval", type=int, default=30, help="Poll interval in seconds (default 30)")

    args = parser.parse_args()

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
