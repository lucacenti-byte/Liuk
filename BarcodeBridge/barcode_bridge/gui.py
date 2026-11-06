from __future__ import annotations

import time


def run_gui(config: dict, *, autostart: bool = True) -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext, ttk
    except ImportError:
        print(
            "tkinter non disponibile. Usa la modalità console:\n"
            "  BarcodeBridge.exe --console\n"
            "  oppure: py -3 -m barcode_bridge --console"
        )
        return 1

    from .core import BarcodeBridge
    from .paths import VERSION

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title(f"BarcodeBridge {VERSION}")
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
                "Modalità batch/GUI: lascia aperta questa finestra. "
                "Per avvio automatico usa installa_avvio_utente.bat "
                "oppure installa_servizio.bat (vedi README)."
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
