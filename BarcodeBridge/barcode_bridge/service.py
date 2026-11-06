"""
Servizio Windows per BarcodeBridge.

Nota importante:
  L'hook tastiera funziona solo nella sessione desktop dell'utente.
  Un servizio CLASSICO (LocalSystem / Session 0) spesso NON vede i tasti
  digitati dall'utente. Per questo:

  1) installa_avvio_utente.bat  → attività Pianificata all'accesso (consigliato)
  2) installa_servizio.bat      → servizio Windows

Comandi (da amministratore):
  BarcodeBridge.exe --service install|start|stop|remove|debug
"""

from __future__ import annotations

import sys


SERVICE_NAME = "BarcodeBridge"
SERVICE_DISPLAY = "BarcodeBridge"
SERVICE_DESCRIPTION = (
    "Intercetta letture barcode HID e rimuove il prefisso fino al carattere '-'."
)


def _ensure_pywin32():
    try:
        import win32event  # noqa: F401
        import win32service  # noqa: F401
        import win32serviceutil  # noqa: F401
        import servicemanager  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "Per la modalità servizio serve pywin32.\n"
            "Esegui installa_dipendenze.bat oppure:\n"
            "  py -3 -m pip install pywin32\n"
            f"Dettaglio: {exc}"
        ) from exc


def _service_class():
    import threading

    import servicemanager
    import win32event
    import win32service
    import win32serviceutil

    from .config import load_config
    from .core import run_worker
    from .logging_setup import setup_logging

    class BarcodeBridgeService(win32serviceutil.ServiceFramework):
        _svc_name_ = SERVICE_NAME
        _svc_display_name_ = SERVICE_DISPLAY
        _svc_description_ = SERVICE_DESCRIPTION

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
            self._python_stop = threading.Event()
            self._thread = None

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self._python_stop.set()
            win32event.SetEvent(self.stop_event)

        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )
            config = load_config()
            setup_logging(config.get("log_level", "INFO"), console=False)

            self._thread = threading.Thread(
                target=run_worker,
                kwargs={"config": config, "stop_event": self._python_stop},
                name="BarcodeBridgeWorker",
                daemon=True,
            )
            self._thread.start()
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            if self._thread is not None:
                self._thread.join(timeout=10)
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, ""),
            )

    return BarcodeBridgeService


def run_service_dispatcher() -> int:
    """Entry point chiamato da SCM: BarcodeBridge.exe --service-run"""
    _ensure_pywin32()
    import servicemanager
    import win32serviceutil

    cls = _service_class()
    if len(sys.argv) == 1 or "--service-run" in sys.argv:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(cls)
        servicemanager.StartServiceCtrlDispatcher()
        return 0
    win32serviceutil.HandleCommandLine(cls)
    return 0


def run_service_command(argv: list[str]) -> int:
    """Gestisce: install | remove | start | stop | restart | debug | update."""
    _ensure_pywin32()
    import win32serviceutil

    if not argv:
        print(
            "Uso: --service [install|remove|start|stop|restart|debug|update]",
            file=sys.stderr,
        )
        return 2

    cls = _service_class()

    # Exe PyInstaller: lo SCM deve rilanciare l'exe con --service-run.
    # Sorgente Python: pywin32 registra python.exe + script (comportamento default).
    if getattr(sys, "frozen", False):
        cls._exe_name_ = sys.executable
        cls._exe_args_ = "--service-run"

    old = sys.argv[:]
    try:
        sys.argv = [old[0], *argv]
        win32serviceutil.HandleCommandLine(cls)
    finally:
        sys.argv = old
    return 0
