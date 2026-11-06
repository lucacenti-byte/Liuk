# BarcodeBridge

Software Windows **autonomo** che intercetta la lettura di un barcode (lettore a emulazione tastiera) e **rimuove il prefisso fino al primo `-`** prima che il testo arrivi al campo del sito web.

```text
ABC1234-9876543210  →  9876543210
```

Può girare in due modi (scegli dopo, entrambi sono già pronti):

| Modalità | Quando usarla | Come |
|----------|---------------|------|
| **Batch / GUI / console** | Avvio manuale o all’accesso utente | `avvia.bat`, `scripts\avvia_console.bat`, `scripts\installa_avvio_utente.bat` |
| **Servizio Windows** | Avvio con il sistema | `scripts\installa_servizio.bat` |

> L’hook tastiera funziona nella **sessione desktop dell’utente**. Per uso quotidiano è più affidabile l’**avvio automatico utente** (attività Pianificata) rispetto a un servizio LocalSystem.

## Distribuzione sui PC

Due strade:

### A) Pacchetto standalone (nessun Python sul PC destinazione)

Su un PC di build con Python:

```bat
scripts\build_standalone.bat
```

Copia l’intera cartella `dist\BarcodeBridge\` su ogni PC (es. `d:\Utility\CURSOR\BarcodeBridge`).

### B) Cartella con ambiente virtuale locale

Su ogni PC con Python 3.10+:

```bat
scripts\installa_dipendenze.bat
```

Crea `.venv` con tutte le dipendenze: la cartella diventa autosufficiente.

## Avvio batch

- `avvia.bat` — interfaccia grafica  
- `scripts\avvia_console.bat` — solo console (adatto a servizio / task)  
- Test senza scanner:  
  `BarcodeBridge.exe --demo ABC1234-9876543210`  
  oppure `py -3 -m barcode_bridge --demo ABC1234-9876543210`

## Avvio automatico / servizio

**Consigliato (sessione utente):**

```bat
scripts\installa_avvio_utente.bat
```

**Servizio Windows** (Amministratore):

```bat
scripts\installa_servizio.bat
scripts\avvia_servizio.bat
scripts\ferma_servizio.bat
scripts\rimuovi_servizio.bat
```

Log: `logs\barcode_bridge.log`

## Configurazione (`config.json`)

| Chiave | Significato | Default |
|--------|-------------|---------|
| `strip_through_dash` | Taglia tutto fino a `-` (incluso) | `true` |
| `require_dash` | Senza `-` lascia passare invariato | `true` |
| `send_enter` | Dopo il codice reinietta Invio | `true` |
| `max_key_interval_ms` | Intervallo max tra tasti (barcode) | `80` |
| `min_barcode_length` | Lunghezza minima sequenza | `5` |
| `log_level` | Livello log file | `INFO` |

## Struttura

```text
BarcodeBridge/
  avvia.bat
  config.json
  requirements.txt
  run_barcode_bridge.py
  barcode_bridge/          ← codice Python
  scripts/                 ← installazione, servizio, build
  logs/                    ← creato a runtime
```

## Requisiti tecnici

- Windows 10/11  
- Lettore barcode in modalità **tastiera (HID)**  
- Per build standalone o sviluppo: Python 3.10+  
- Eventualmente “Esegui come amministratore” se l’hook non intercetta
