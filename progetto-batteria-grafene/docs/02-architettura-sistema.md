# 2. Architettura di sistema

## 2.1 Schema a blocchi

```
                    ┌─────────────┐
   sole ───────────▶│  Campo PV   │
                    └──────┬──────┘
                           │ DC
                    ┌──────▼──────┐
                    │ MPPT / PCS  │◀── rete (opz.)
                    └──┬──────┬───┘
               DC bus  │      │ AC
         ┌─────────────▼┐     └────────▶ carichi
         │  LGGS Daily  │
         │  (rack BMS)  │
         └──────┬───────┘
                │ trasferimento controllato
         ┌──────▼───────┐
         │ LGGS Vault   │  ◀── vuoto + T stabilizzata
         │ (stagionale) │
         └──────────────┘
```

Schema Mermaid: [`../schematics/sistema.mmd`](../schematics/sistema.mmd).

## 2.2 Livelli

### Livello 0 — Campo PV

Stringhe / ottimizzatori, inverter ibrido o PCS DC-coupled. Il surplus oltre autoconsumo e carica daily va al vault (se abilitato) o in rete/curtamento.

### Livello 1 — LGGS Daily Rack

- Moduli pouch 48 V o 400 V (HV) in serie/parallelo
- BMS master + slave per stringa
- Contattori, fusibili, precarica, HVAC cabinet
- Ciclo tipico: DoD 60–80%, 1 ciclo/giorno

### Livello 2 — LGGS Seasonal Vault

- Stesso formato di modulo, ma **policy diversa**:
  - carica lenta in estate (C/10–C/20) fino a SOC target 60–70%
  - trasferimento in vault: T = 15–20 °C, UR &lt; 40%, monitoraggio pressione pouch
  - scarica invernale a C/20–C/5 verso bus DC / inverter
- Obiettivo: massimizzare vita calendario, non potenza

### Livello 3 — EMS (Energy Management System)

Regole tipiche:

1. Priorità: carico → daily → vault → rete/export
2. Mai scaricare il vault se daily ha margine
3. In estate: se daily SOC &gt; 90% e PV surplus &gt; soglia → carica vault
4. In inverno: se daily SOC &lt; 20% e carico &gt; PV → scarica vault
5. Equalizzazione mensile e bilanciamento celle

## 2.3 Topologie di connessione

| Topologia | Pro | Contro | Uso consigliato |
|---|---|---|---|
| DC-coupled | meno conversioni, RTE migliore | integrazione OEM più stretta | nuovi impianti |
| AC-coupled | retrofit semplice | −3…6% RTE | impianti esistenti |
| Ibrida | flessibilità | complessità EMS | comunità energetiche |

## 2.4 Dimensioni di riferimento

| Scala | PV | Daily | Vault |
|---|---|---|---|
| Casa | 6 kWp | 10–15 kWh | 0–30 kWh |
| PMI | 50 kWp | 50–100 kWh | 100–300 kWh |
| Agrivoltaico / farm | 500 kWp | 0.5–1 MWh | 1–5 MWh (+ eventuale P2X) |

Il tool `sim/energy_balance.py` calcola questi ordini di grandezza da consumo e irraggiamento.

## 2.5 Interfacce

- **Elettriche**: DC bus nominale (es. 400–800 V), contatti di potenza, PE
- **Dati**: Modbus TCP / CAN BMS → EMS → SCADA
- **Sicurezza**: EPO, smoke/gas (se litio), isolamento, ground fault
- **Meccaniche**: rack 19"/cabinet IP54, vault isolato termicamente

## 2.6 Flusso energetico tipico (giorno estivo)

1. Mattina: PV → carico + carica daily
2. Mezzogiorno: daily pieno → surplus → vault (lento) o export
3. Sera: PV cala → daily alimenta carichi
4. Notte: solo daily (vault idle)

Inverno: vault fornisce energia residua al daily o direttamente al bus quando il PV è insufficiente per più giorni.