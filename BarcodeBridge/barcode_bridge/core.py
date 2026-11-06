from __future__ import annotations

import logging
import threading
import time

from .strip import strip_prefix

try:
    import keyboard
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Manca il modulo 'keyboard'. Esegui installa_dipendenze.bat "
        "oppure: py -3 -m pip install -r requirements.txt"
    ) from exc

logger = logging.getLogger("barcode_bridge")


class BarcodeBridge:
    """
    Hook globale tastiera (Windows, sessione utente interattiva).

    Ogni tasto viene soppresso e messo in buffer. Se entro max_key_interval_ms
    non arriva nulla, il buffer viene rilasciato come digitazione normale.
    Se arriva Invio e il buffer sembra un barcode, viene applicato lo strip.
    """

    def __init__(self, config: dict, on_event=None):
        self.config = config
        self.on_event = on_event or self._default_event
        self._buffer: list[str] = []
        self._injecting = False
        self._running = False
        self._lock = threading.Lock()
        self._flush_timer: threading.Timer | None = None
        self._unhook = None

    @staticmethod
    def _default_event(kind: str, message: str) -> None:
        if kind == "transformed":
            logger.info("Trasformato: %s", message)
        elif kind == "passthrough":
            logger.info("Passthrough: %s", message)
        elif kind == "status":
            logger.info("%s", message)
        else:
            logger.debug("[%s] %s", kind, message)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        # suppress=True: callback False = blocca, True = lascia passare
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
        if self._injecting or not self._running:
            return True

        name = (event.name or "").lower()

        if event.event_type != keyboard.KEY_DOWN:
            with self._lock:
                capturing = bool(self._buffer)
            return not capturing

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
                    return not bool(self._buffer)
                if self._buffer:
                    self._cancel_timer()
                    self._release_buffer_locked(as_enter=False)
                return True

            self._buffer.append(char)
            self._arm_timer_locked()
            return False

    @staticmethod
    def _has_modifier_combo(name: str) -> bool:
        if name in (
            "ctrl",
            "left ctrl",
            "right ctrl",
            "alt",
            "left alt",
            "right alt",
            "windows",
            "cmd",
        ):
            return False
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


def run_worker(config: dict, *, stop_event: threading.Event | None = None) -> None:
    """Avvia il bridge e resta in esecuzione fino a stop_event o KeyboardInterrupt."""
    bridge = BarcodeBridge(config)
    bridge.start()
    try:
        if stop_event is None:
            while True:
                time.sleep(0.5)
        else:
            while not stop_event.wait(0.5):
                pass
    finally:
        bridge.stop()
