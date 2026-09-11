# 3. Cella, gel e packaging sotto vuoto

## 3.1 Concetto di cella

Cella **pouch** a elettrodi di grafene strutturato, immersi/impregnati in **elettrolita gel quasi-solido**, chiusa sotto **vuoto** in laminato barriera.

Due chimiche candidate (fase di down-select):

| Variante | Anodo | Catodo | Ruolo |
|---|---|---|---|
| **G-LFP** (preferita stazionario) | grafene / Si-grafene o grafite+grafene | LiFePO₄ con rete grafene | energia, sicurezza, cicli |
| **G-Hybrid** | grafene (EDLC) | grafene / ossido metallico | potenza + buffer rapido |

Per PV notturno e vault: **G-LFP** come baseline. G-Hybrid come modulo “power” affiancato se servono picchi.

## 3.2 Perché il grafene

- Alta superficie specifica → interfaccia elettrodo/elettrolita ampia
- Conducibilità elettronica → meno nero di carbonio, elettrodo più “attivo”
- Rete meccanica → limita cracking (utile con Si o LFP ad alto loading)
- Conduzione termica → hotspot ridotti nel modulo

Forme: rGO (reduced graphene oxide), few-layer graphene, graphene nanoplatelets (GNP). Per lab: GNP + rGO blend è il compromesso costi/prestazioni più realistico.

## 3.3 Elettrolita gel

Obiettivo: immobilizzare il solvente, ridurre leakage e combustibilità, mantenere σ ionica accettabile.

**Formulazione di partenza (lab):**

- Matrice polimerica: PVDF-HFP o PEO / PVA (in base a solvente)
- Sale: LiTFSI o LiFSI (1 M eq. in fase liquida impregnante)
- Plastificante / liquido ionico (opz.): EMIM-TFSI per allargare finestra T e ridurre volatilità
- Additivi SEI: FEC 2–5% vol (se anodo Si/grafite)
- Carica di filler ceramico (opz.): Al₂O₃ / LLZO nano 5–10 wt% per tortuosità e stabilità

**Processo:**

1. Dissoluzione polimero + sale
2. Casting / impregnazione elettrodi (o gel in-situ termico/UV)
3. Assemblaggio sandwich anodo | gel | catodo
4. Degassing
5. Sigillatura pouch sotto vuoto

Target conducibilità gel a 25 °C: **≥ 1 mS/cm** (accettabile per C/5–1C stazionario).

## 3.4 Packaging sotto vuoto

### Perché il vuoto

- Rimuove O₂ e umidità residua → meno reazioni parassite e autoscarica
- Riduce gas intrappolati → meno swelling
- Migliora contatto elettrodo–gel (pressione atmosferica esterna sul pouch flessibile)
- Favorisce **shelf-life** del vault stagionale

### Parametri target

| Parametro | Valore |
|---|---|
| Vuoto residuo pre-sigillo | ≤ 10 mbar (ideale 1–5 mbar) |
| Laminato | Al-PET-PP / nylon-Al-PP spessore tipico 113–153 μm |
| Leak rate | ≈ 0 (test He o decadimento pressione 24–72 h) |
| Tab | nickel / alluminio con sealant |
| Sensore opzionale | micro pressure / strain per swelling |

### Sequenza di fabbricazione modulo

1. Taglio elettrodi e tab welding
2. Stack + gel
3. Pre-seal a 3 lati
4. Riempimento/impregnazione se gel non già in-situ
5. **Vacuum seal** lato restante
6. Formazione elettrochimica (cicli lenti)
7. Degassing secondario + ri-sigillo (se gassing)
8. Test capacità, IR, isolamento
9. Assemblaggio in modulo + BMS slave

## 3.5 Parametri elettrici cella (target lab 10 Ah)

| Voce | Valore |
|---|---|
| Capacità nominale | 10 Ah |
| Tensione nominale | 3,2 V (G-LFP) |
| Energia cella | ≈ 32 Wh |
| Vmin / Vmax | 2,5 / 3,65 V |
| Corrente continua | 0,2–0,5 C (vault/daily) |
| Impedenza AC 1 kHz | &lt; 5 mΩ (target) |
| Formato | pouch ≈ 8×150×200 mm (ordine di grandezza) |

Stack modulo 48 V: 15s Np → ~480 Wh per stringa base (con N paralleli).

## 3.6 Autoscarica e vault

Meccanismi da contenere:

- Reazioni elettroniche parassite (umidità, O₂)
- Micro-short da dendriti / contaminazione
- Redox shuttle in elettrolita

Mitigazioni LGGS:

- Gel a bassa mobilità di impurezze
- Vacuum + laminato barriera
- SOC vault 50–70% (non 100%)
- T vault 15–20 °C
- Bilanciamento passivo/attivo periodico

KPI: **≤ 1%/mese** a 20 °C in vault (obiettivo TRL5); ≤ 3%/mese accettabile in TRL3.

## 3.7 Prove di laboratorio essenziali

1. σ ionica gel (EIS) vs T
2. Cicli 0,2C/0,2C a 25 °C — fade capacità
3. Autoscarica: carica a SOC 70%, open circuit 30/60/90 giorni
4. Abuse: overcharge, short, crush (scala cella)
5. Vacuum integrity: immersione / He leak
6. Thermal runaway screening (ARC o hot-box) su G-LFP

## 3.8 Nota realistica

Il “grafene sospeso nel gel sotto vuoto” è una **architettura di packaging + elettrodo**, non una nuova legge fisica. Le prestazioni dipendono da loading, porosità, interfaccia gel e purezza. Il progetto punta a dimostrare che questa combinazione migliora **sicurezza + shelf-life**, abilitando il caso stagionale meglio di una cella liquida convenzionale non ottimizzata.