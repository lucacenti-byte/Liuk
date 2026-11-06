from __future__ import annotations

import argparse
import sys

from .config import load_config
from .logging_setup import setup_logging
from .paths import APP_DIR, VERSION
from .strip import strip_prefix


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)

    # Avvio dal Service Control Manager
    if "--service-run" in raw_argv:
        from .service import run_service_dispatcher

        return run_service_dispatcher()

    parser = argparse.ArgumentParser(
        prog="BarcodeBridge",
        description="Intercetta barcode HID e rimuove il prefisso fino a '-'.",
    )
    parser.add_argument("--version", action="version", version=f"BarcodeBridge {VERSION}")
    parser.add_argument(
        "--demo",
        metavar="CODICE",
        help="Mostra solo la trasformazione, senza intercettare la tastiera",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Modalità batch/console senza GUI (Ctrl+C per uscire)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Forza la GUI (default se non è --console/--service)",
    )
    parser.add_argument(
        "--no-autostart",
        action="store_true",
        help="Apri la GUI senza avviare subito l'intercettazione",
    )
    parser.add_argument(
        "--service",
        nargs=argparse.REMAINDER,
        help="Comandi servizio Windows: install|remove|start|stop|restart|debug",
    )
    args = parser.parse_args(raw_argv)
    config = load_config()

    if args.demo is not None:
        cleaned = strip_prefix(
            args.demo,
            strip_through_dash=bool(config["strip_through_dash"]),
            require_dash=bool(config["require_dash"]),
        )
        if cleaned is None:
            print(f"Nessuna trasformazione: {args.demo}")
        else:
            print(f"{args.demo}  →  {cleaned}")
        return 0

    if args.service is not None:
        # argparse.REMAINDER include un eventuale '--' iniziale
        svc_args = [a for a in args.service if a != "--"]
        from .service import run_service_command

        return run_service_command(svc_args)

    setup_logging(config.get("log_level", "INFO"), console=True)

    if args.console and not args.gui:
        from .core import run_worker

        print(f"BarcodeBridge {VERSION} — console")
        print(f"Cartella: {APP_DIR}")
        print("Ctrl+C per uscire.")
        try:
            run_worker(config)
        except KeyboardInterrupt:
            print("\nUscita…")
        return 0

    from .gui import run_gui

    return run_gui(config, autostart=not args.no_autostart)


if __name__ == "__main__":
    raise SystemExit(main())
