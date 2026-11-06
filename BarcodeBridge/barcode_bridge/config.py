from __future__ import annotations

import json
import logging

from .paths import CONFIG_PATH

DEFAULT_CONFIG = {
    "max_key_interval_ms": 80,
    "min_barcode_length": 5,
    "strip_through_dash": True,
    "require_dash": True,
    "send_enter": True,
    "log_passthrough": False,
    "log_level": "INFO",
}


def load_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open(encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                cfg.update(loaded)
        except (OSError, json.JSONDecodeError) as exc:
            logging.getLogger("barcode_bridge").warning(
                "config.json non valido (%s), uso default.", exc
            )
    return cfg
