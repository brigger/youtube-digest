"""Config loading and saving for ytdigest."""

import sys
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ytdigest" / "config.yaml"


def _migrate(cfg: dict) -> dict:
    """Convert old single-channel format to new sources/topics format (in memory only)."""
    if "channel" in cfg and "sources" not in cfg:
        channel = cfg.pop("channel")
        count = cfg.pop("count", 3)
        cfg["sources"] = [
            {
                "url": channel,
                "type": "youtube",
                "name": channel,
                "count": count,
            }
        ]
    if "topics" not in cfg:
        cfg["topics"] = []
    return cfg


def load(path: Path | None = None) -> dict:
    p = path or DEFAULT_CONFIG_PATH
    if not p.exists():
        sys.exit(
            f"Config not found: {p}\n"
            "Run `ytdigest init` to create one, or pass --config <path>."
        )
    with open(p) as f:
        cfg = yaml.safe_load(f)
    return _migrate(cfg)


def save(cfg: dict, path: Path | None = None) -> None:
    p = path or DEFAULT_CONFIG_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Config saved to {p}")
