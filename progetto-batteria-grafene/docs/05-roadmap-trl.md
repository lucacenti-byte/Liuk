# 5. Roadmap TRL, BOM e costi

## 5.1 Fasi

| Fase | TRL | Obiettivo | Deliverable |
|---|---|---|---|
| F0 Concept | 1–2 | dossier, KPI, rischi | questo repository |
| F1 Materiali | 2–3 | gel σ≥1 mS/cm; elettrodi casting | report EIS, SEM |
| F2 Cella | 3 | pouch 1–10 Ah vacuum-sealed | ≥200 cicli, RTE≥88% |
| F3 Modulo | 4 | 1–5 kWh + BMS | test notturno su carico reale |
| F4 Vault demo | 4–5 | 10–30 kWh, 90 giorni shelf | autoscarica misurata |
| F5 Pilota campo | 6–7 | integrazione PV 6–50 kWp | EMS, CE prep |
| F6 Industrializzazione | 7–8 | supply chain GNP/LFP/gel | DfM, costi target |

## 5.2 BOM laboratorio (F2) — ordine di grandezza

| Voce | Specifica | Nota |
|---|---|---|
| GNP / rGO | grado batteria | elettrodo |
| LFP | battery grade | catodo |
| Binder | PVDF / CMC-SBR | |
| Sale LiTFSI | battery grade | gel |
| Polimero gel | PVDF-HFP / PEO | |
| Laminato pouch | Al multi-layer | |
| Tab Ni/Al | con sealant | |
| Vacuum sealer | camera o barra | tool |
| cycler | 5 V / 10–20 A | test |
| Glovebox / dry room | H₂O &lt; 10–50 ppm | qualità |

Costo setup lab minimale (senza glovebox full): decine di k€. Con dry room / cycler multi-canale: centinaia di k€.

## 5.3 Costi sistema (ordine di grandezza, non quotazione)

| Voce | Oggi (stima R&D) | Target pilota |
|---|---|---|
| Cella G-LFP gel | 250–400 €/kWh | 150–220 €/kWh |
| Modulo+BMS+cabinet | +80–150 €/kWh | +50–80 €/kWh |
| Vault HVAC + monitoring | 5–20 k€ (piccolo) | scalabile |
| EMS / integrazione | 2–10 k€ | pack software |

Confrontare sempre con LFP liquido commerciale (~100–200 €/kWh pack stazionario maturo): LGGS si giustifica se **shelf-life / sicurezza / cicli** ripagano il premium.

## 5.4 Team minimo

- Electrochemist (gel + formazione)
- Materials (grafene, elettrodi)
- Mechanical / packaging (pouch, vacuum)
- Power electronics / BMS
- EMS / PV systems engineer
- Safety & compliance

## 5.5 Gate di go/no-go

| Gate | Criterio |
|---|---|
| G1 | gel σ e stabilità 30 giorni OK |
| G2 | cella 10 Ah: 200 cicli, fade &lt; 15% |
| G3 | autoscarica 90 giorni ≤ 3%/mese |
| G4 | modulo 5 kWh: RTE sistema ≥ 85% su ciclo notturno reale |
| G5 | business case vs LFP liquido su caso d’uso vault |