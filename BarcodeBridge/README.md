# BarcodeBridge

Programma Python per Windows che intercetta la lettura di un barcode (lettore a emulazione tastiera) e **rimuove il prefisso fino al primo carattere `-`** prima che il testo arrivi al campo del sito web.

Esempio:

```text
ABC1234-9876543210  →  9876543210
```

I primi caratteri (tipicamente 7) e il `-` non vengono più digitati: sul sito compare solo la parte utile.

## Requisiti

- Windows
- Python 3.10+
- Lettore barcode in modalità **tastiera (HID / keyboard wedge)**

## Installazione

Copia questa cartella in `d:\Utility\CURSOR\BarcodeBridge` (o dovunque preferisci), poi:

```bat
cd /d d:\Utility\CURSOR\BarcodeBridge
py -3 -m pip install -r requirements.txt
```

## Avvio

Doppio clic su `avvia.bat`, oppure:

```bat
py -3 barcode_bridge.py
```

Se l’intercettazione non funziona, avvia **come amministratore** (clic destro → Esegui come amministratore).

1. Lascia aperta la finestra BarcodeBridge  
2. Metti il cursore sul campo del sito web  
3. Scansiona il barcode  

Nel log vedrai `originale → trasformato`.

## Test senza scanner

Nella GUI usa il campo **Test manuale**, oppure da console:

```bat
py -3 barcode_bridge.py --demo ABC1234-9876543210
```

## Configurazione (`config.json`)

| Chiave | Significato | Default |
|--------|-------------|---------|
| `strip_through_dash` | Taglia tutto fino a `-` (incluso) | `true` |
| `require_dash` | Se non c’è `-`, lascia passare la lettura invariata | `true` |
| `send_enter` | Dopo il codice reinietta anche Invio | `true` |
| `max_key_interval_ms` | Intervallo massimo tra tasti per riconoscerli come barcode | `80` |
| `min_barcode_length` | Lunghezza minima per trattare la sequenza come barcode | `5` |

## Note

- La digitazione normale (lenta) non viene alterata: solo sequenze rapide tipiche dello scanner.
- Il programma deve restare in esecuzione mentre usi il sito.
- Non modifica il lettore: filtra solo ciò che arriva alla tastiera virtuale.
