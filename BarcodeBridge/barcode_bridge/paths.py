from __future__ import annotations

import sys
from pathlib import Path

VERSION = "1.1.0"


def app_dir() -> Path:
    """
    Cartella dati del programma (config, log).
    Con PyInstaller punta alla cartella dell'eseguibile; altrimenti a BarcodeBridge/.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # Pacchetto in BarcodeBridge/barcode_bridge/ → root distribuzione = parent
    return Path(__file__).resolve().parent.parent


APP_DIR = app_dir()
CONFIG_PATH = APP_DIR / "config.json"
LOG_DIR = APP_DIR / "logs"
LOG_FILE = LOG_DIR / "barcode_bridge.log"
