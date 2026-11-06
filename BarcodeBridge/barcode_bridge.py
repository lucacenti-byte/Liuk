#!/usr/bin/env python3
"""
BarcodeBridge — intercetta letture barcode (tastiera HID) e rimuove
il prefisso fino al primo carattere '-', inviando al sito solo il resto.

Esempio:  ABC1234-9876543210  →  9876543210

Su Windows il lettore barcode digita molto velocemente e termina con Invio.
Questo programma sopprime quella sequenza, toglie tutto fino a '-' (incluso)
e reinietta solo la parte restante nel campo attivo (es. sito web).
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from pathlib import Path

try:
    import keyboard
except ImportError:
    print(
        "Manca il modulo 'keyboard'. Installa con:\n"
        "  py -3 -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "config.json"

DEFAULT_CONFIG = {
    "max_key_interval_ms": 80,
    "min_barcode_length": 5,
    "strip_through_dash": True,
    "require_dash": True,
    "send_enter": True,
    "log_passthrough": False,
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
            print(f"Attenzione: config.json non valido ({exc}), uso default.")
    return cfg


def strip_prefix(raw: str, *, strip_through_dash: bool = True, require_dash: bool = True) -> str | None:
    """
    Rimuove tutto fino al primo '-' (incluso) e restituisce il resto.

    Restituisce None se la lettura non va trasformata (va lasciata passare
    così com'è), ad esempio se manca '-' e require_dash=True.
    """
    raw = raw.strip()
    if not raw:
        return None

    if strip_through_dash:
        if "-" not in raw:
            return None if require_dash else raw
        return raw.split("-", 1)[1]

    # Fallback: togli i primi 7 caratteri
    if len(raw) <= 7:
        return None if require_dash else raw
    return raw[7:]


class BarcodeBridge:
    """
    Hook globale tastiera (Windows).

    Ogni tasto viene soppresso e messo in buffer. Se entro max_key_interval_ms
    non arriva nulla, il buffer viene rilasciato come digitazione normale.
    Se arriva Invio e il buffer sembra un barcode, viene applicato lo strip.
    """

    def __init__(self, config: dict, on_event=None):
        self.config = config
        self.on_event = on_event or (lambda *_: None)
        self._buffer: list[str] = []
        self._injecting = False
        self._running = False
        self._lock = threading.Lock()
        self._flush_timer: threading.Timer | None = None
        self._unhook = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        # Con suppress=True: callback False = blocca, True = lascia passare
        self._unhook = keyboard.hook(self._on_key, suppress=True)
        self.on_event("status", "In ascolto dei barcode…")

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        self._cancel_timer()
        if self._unhook is not None:
            try:
                self._unhook()
            except Exception:
                keyboard.unhook_all()
            self._unhook = None
        with self._lock:
            self._release_buffer_locked(as_enter=False)
        self.on_event("status", "Fermato.")

    def process_manual(self, raw: str) -> str:
        cleaned = strip_prefix(
            raw,
            strip_through_dash=bool(self.config["strip_through_dash"]),
            require_dash=bool(self.config["require_dash"]),
        )
        if cleaned is None:
            self.on_event("passthrough", raw)
            return raw
        self.on_event("transformed", f"{raw}  →  {cleaned}")
        return cleaned

    def _on_key(self, event: keyboard.KeyboardEvent) -> bool:
        # True = lascia passare l'evento; False = sopprimilo
        if self._injecting or not self._running:
            return True

        name = (event.name or "").lower()

        # Durante la cattura blocchiamo anche i key-up dei caratteri bufferizzati
        if event.event_type != keyboard.KEY_DOWN:
            with self._lock:
                capturing = bool(self._buffer)
            return not capturing

        # Non interferire con scorciatoie (Ctrl/Alt/Win + tasto)
        if self._has_modifier_combo(name):
            with self._lock:
                if self._buffer:
                    self._cancel_timer()
                    self._release_buffer_locked(as_enter=False)
            return True

        with self._lock:
            if name in ("enter", "return"):
                self._cancel_timer()
                self._finalize_locked()
                return False

            char = self._event_to_char(name)
            if char is None:
                if name in ("shift", "left shift", "right shift", "caps lock"):
                    # Gli scanner a volte mandano Shift per le maiuscole:
                    # se stiamo già catturando, sopprimi; altrimenti passa.
                    return not bool(self._buffer)
                # Altri tasti speciali: rilascia eventuale buffer e lascia passare
                if self._buffer:
                    self._cancel_timer()
                    self._release_buffer_locked(as_enter=False)
                return True

            self._buffer.append(char)
            self._arm_timer_locked()
            return False

    @staticmethod
    def _has_modifier_combo(name: str) -> bool:
        if name in ("ctrl", "left ctrl", "right ctrl", "alt", "left alt", "right alt", "windows", "cmd"):
            return False  # gestiti come speciali sopra / sotto
        try:
            return (
                keyboard.is_pressed("ctrl")
                or keyboard.is_pressed("alt")
                or keyboard.is_pressed("windows")
            )
        except Exception:
            return False

    @staticmethod
    def _event_to_char(name: str) -> str | None:
        if len(name) == 1:
            return name
        aliases = {
            "space": " ",
            "minus": "-",
            "dash": "-",
            "-": "-",
        }
        return aliases.get(name)

    def _arm_timer_locked(self) -> None:
        self._cancel_timer()
        delay = self.config["max_key_interval_ms"] / 1000.0
        timer = threading.Timer(delay, self._on_idle_timeout)
        timer.daemon = True
        self._flush_timer = timer
        timer.start()

    def _cancel_timer(self) -> None:
        timer = self._flush_timer
        self._flush_timer = None
        if timer is not None:
            timer.cancel()

    def _on_idle_timeout(self) -> None:
        with self._lock:
            if not self._running:
                return
            self._flush_timer = None
            if self._buffer:
                if self.config.get("log_passthrough"):
                    self.on_event("passthrough", "".join(self._buffer))
                self._release_buffer_locked(as_enter=False)

    def _finalize_locked(self) -> None:
        raw = "".join(self._buffer)
        self._buffer.clear()
        min_len = int(self.config["min_barcode_length"])

        if len(raw) < min_len:
            self._type_text(raw)
            if self.config["send_enter"]:
                self._type_enter()
            return

        cleaned = strip_prefix(
            raw,
            strip_through_dash=bool(self.config["strip_through_dash"]),
            require_dash=bool(self.config["require_dash"]),
        )

        if cleaned is None:
            self.on_event("passthrough", raw)
            self._type_text(raw)
            if self.config["send_enter"]:
                self._type_enter()
            return

        self.on_event("transformed", f"{raw}  →  {cleaned}")
        self._type_text(cleaned)
        if self.config["send_enter"]:
            self._type_enter()

    def _release_buffer_locked(self, *, as_enter: bool) -> None:
        raw = "".join(self._buffer)
        self._buffer.clear()
        if raw:
            self._type_text(raw)
        if as_enter and self.config["send_enter"]:
            self._type_enter()

    def _type_text(self, text: str) -> None:
        if not text:
            return
        self._injecting = True
        try:
            keyboard.write(text, delay=0)
        finally:
            threading.Timer(0.08, self._clear_injecting).start()

    def _type_enter(self) -> None:
        self._injecting = True
        try:
            keyboard.press_and_release("enter")
        finally:
            threading.Timer(0.08, self._clear_injecting).start()

    def _clear_injecting(self) -> None:
        self._injecting = False


def run_gui(config: dict, *, autostart: bool = True) -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext, ttk
    except ImportError:
        print(
            "tkinter non disponibile. Avvia in modalità console:\n"
            "  py -3 barcode_bridge.py --no-gui",
            file=sys.stderr,
        )
        return 1

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("BarcodeBridge")
            self.geometry("640x420")
            self.minsize(520, 360)
            self.configure(bg="#1a2332")
            self.bridge = BarcodeBridge(config, on_event=self._on_bridge_event)
            self._build_ui()
            self.protocol("WM_DELETE_WINDOW", self._on_close)
            if autostart:
                self.after(200, self._start)

        def _build_ui(self) -> None:
            style = ttk.Style(self)
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass

            header = tk.Frame(self, bg="#1a2332")
            header.pack(fill="x", padx=16, pady=(16, 8))
            tk.Label(
                header,
                text="BarcodeBridge",
                font=("Segoe UI Semibold", 18),
                fg="#f0f4f8",
                bg="#1a2332",
            ).pack(anchor="w")
            tk.Label(
                header,
                text="Rimuove il prefisso fino a '-' prima che la lettura arrivi al sito.",
                font=("Segoe UI", 10),
                fg="#9fb0c3",
                bg="#1a2332",
            ).pack(anchor="w", pady=(2, 0))

            controls = tk.Frame(self, bg="#1a2332")
            controls.pack(fill="x", padx=16, pady=8)
            self.status_var = tk.StringVar(value="Pronto.")
            self.btn_start = ttk.Button(controls, text="Avvia", command=self._start)
            self.btn_stop = ttk.Button(controls, text="Ferma", command=self._stop, state="disabled")
            self.btn_start.pack(side="left")
            self.btn_stop.pack(side="left", padx=(8, 0))
            tk.Label(
                controls,
                textvariable=self.status_var,
                font=("Segoe UI", 10),
                fg="#7dd3a7",
                bg="#1a2332",
            ).pack(side="left", padx=(16, 0))

            test = tk.LabelFrame(
                self,
                text="  Test manuale  ",
                font=("Segoe UI", 9),
                fg="#9fb0c3",
                bg="#1a2332",
                bd=1,
                relief="groove",
            )
            test.pack(fill="x", padx=16, pady=(4, 8))
            row = tk.Frame(test, bg="#1a2332")
            row.pack(fill="x", padx=10, pady=10)
            self.test_entry = ttk.Entry(row)
            self.test_entry.pack(side="left", fill="x", expand=True)
            self.test_entry.insert(0, "ABC1234-9876543210")
            ttk.Button(row, text="Prova", command=self._run_test).pack(side="left", padx=(8, 0))

            self.log = scrolledtext.ScrolledText(
                self,
                height=12,
                font=("Consolas", 10),
                bg="#0f1620",
                fg="#d7e2ee",
                insertbackground="#d7e2ee",
                relief="flat",
                wrap="word",
            )
            self.log.pack(fill="both", expand=True, padx=16, pady=(0, 16))
            self.log.configure(state="disabled")
            self.log.tag_configure("transformed", foreground="#7dd3a7")
            self.log.tag_configure("passthrough", foreground="#e6c07b")
            self.log.tag_configure("status", foreground="#9fb0c3")
            self.log.tag_configure("error", foreground="#f07178")

            tip = (
                "Lascia questa finestra aperta, metti il focus sul campo del sito "
                "e scansiona. Su Windows, se non intercetta, avvia come amministratore. "
                "Mentre è attivo, la digitazione normale ha un piccolo ritardo (~80 ms)."
            )
            tk.Label(
                self,
                text=tip,
                font=("Segoe UI", 8),
                fg="#6b7c8f",
                bg="#1a2332",
                wraplength=600,
                justify="left",
            ).pack(fill="x", padx=16, pady=(0, 12))

        def _append_log(self, kind: str, message: str) -> None:
            stamp = time.strftime("%H:%M:%S")
            self.log.configure(state="normal")
            tag = kind if kind in ("transformed", "passthrough", "status", "error") else "status"
            self.log.insert("end", f"[{stamp}] {message}\n", tag)
            self.log.see("end")
            self.log.configure(state="disabled")

        def _on_bridge_event(self, kind: str, message: str) -> None:
            self.after(0, lambda: self._handle_event(kind, message))

        def _handle_event(self, kind: str, message: str) -> None:
            if kind == "status":
                self.status_var.set(message)
            self._append_log(kind, message)

        def _start(self) -> None:
            try:
                self.bridge.start()
            except Exception as exc:
                self._append_log("error", f"Errore avvio: {exc}")
                messagebox.showerror(
                    "BarcodeBridge",
                    "Impossibile intercettare la tastiera.\n"
                    "Prova ad avviare come Amministratore.\n\n"
                    f"Dettaglio: {exc}",
                )
                return
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")

        def _stop(self) -> None:
            self.bridge.stop()
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")

        def _run_test(self) -> None:
            raw = self.test_entry.get().strip()
            if not raw:
                return
            result = self.bridge.process_manual(raw)
            self._append_log("status", f"Test risultato: {result}")

        def _on_close(self) -> None:
            try:
                self.bridge.stop()
            finally:
                self.destroy()

    App().mainloop()
    return 0


def run_cli_demo(sample: str, config: dict) -> int:
    cleaned = strip_prefix(
        sample,
        strip_through_dash=bool(config["strip_through_dash"]),
        require_dash=bool(config["require_dash"]),
    )
    if cleaned is None:
        print(f"Nessuna trasformazione: {sample}")
        return 0
    print(f"{sample}  →  {cleaned}")
    return 0


def run_console(config: dict) -> int:
    bridge = BarcodeBridge(
        config,
        on_event=lambda kind, msg: print(f"[{kind}] {msg}", flush=True),
    )
    bridge.start()
    print("BarcodeBridge attivo. Ctrl+C per uscire.", flush=True)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nUscita…")
    finally:
        bridge.stop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BarcodeBridge — strip prefisso fino a '-'")
    parser.add_argument(
        "--demo",
        metavar="CODICE",
        help="Mostra solo la trasformazione senza intercettare la tastiera",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Solo console (intercetta tastiera, Ctrl+C per uscire)",
    )
    parser.add_argument(
        "--no-autostart",
        action="store_true",
        help="Apri la GUI senza avviare subito l'intercettazione",
    )
    args = parser.parse_args(argv)
    config = load_config()

    if args.demo is not None:
        return run_cli_demo(args.demo, config)
    if args.no_gui:
        return run_console(config)
    return run_gui(config, autostart=not args.no_autostart)


if __name__ == "__main__":
    raise SystemExit(main())
