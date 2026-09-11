# 1. Visione e obiettivi

## 1.1 Problema

Un impianto fotovoltaico produce di giorno e in estate in eccesso; la domanda punta di notte e in inverno. Serve un accumulo che:

- gestisca il **disaccoppiamento giornaliero** (ore),
- possa scalare verso il **disaccoppiamento stagionale** (mesi),
- sia più sicuro e stabile di celle liquide tradizionali (minori perdite di elettrolita, packaging robusto).

## 1.2 Soluzione proposta (LGGS)

**Liuk Graphene Gel Storage**: moduli elettrochimici ibridi (capacità + potenza) con:

- **anodo/catodo** a base grafene (rete 3D ad alta superficie specifica),
- **elettrolita in gel** (polimero + sale litio o liquido ionico gelificato),
- **sigillatura sotto vuoto** del pouch (rimozione O₂/H₂O, riduzione gas e ossidazione),
- **gestione a due livelli**: rack giornaliero + vault stagionale.

Il grafene non è “magia”: aumenta conducibilità, superficie e ciclabilità. Il gel riduce perdite e rischi di spill. Il vuoto migliora shelf-life e stabilità chimica — critici per la conservazione estiva→invernale.

## 1.3 Casi d’uso

| Caso | Orizzonte | Priorità tecniche |
|---|---|---|
| A — Residenziale / PMI notturno | 12–48 h | densità energia, cicli >4000, DoD 80% |
| B — Comunità energetica / farm PV | giorni–settimane | modularità, BMS parallelo, costi €/kWh |
| C — Stagionale estate→inverno | 3–6 mesi | autoscarica &lt;1%/mese, vault T/RH controllati |

## 1.4 Requisiti di sistema (target di progetto)

### Funzionali

- Accoppiamento DC o AC con inverter ibrido / PCS
- Carica da eccedenza PV, scarica su carico o rete
- Modalità “daily buffer” e “seasonal vault”
- Telemetria SOC, SOH, T, pressione pouch, isolamento

### Prestazioni target (cellula lab → modulo)

| KPI | Target lab (TRL3) | Target modulo (TRL5) |
|---|---|---|
| Densità energia gravimetrica | ≥ 120 Wh/kg | ≥ 160 Wh/kg |
| Densità potenza | ≥ 300 W/kg | ≥ 500 W/kg |
| Efficienza round-trip | ≥ 88% | ≥ 92% |
| Autoscarica a 25 °C | ≤ 3%/mese | ≤ 1%/mese (vault) |
| Cicli a 80% DoD | ≥ 2000 | ≥ 5000 |
| Range T operativa | −10…+45 °C | −20…+50 °C |
| Vita calendario vault | — | ≥ 6 mesi a SOC 50–70% |

### Non funzionali

- Chimica senza cobalto preferita (LFP + grafene o ibrido EDLC)
- Packaging pouch alluminio laminato, vacuum ≤ 10 mbar residui
- Conformità CE / IEC 62619 (stazionario) come obiettivo di fase 4+

## 1.5 Cosa non promette questo dossier

- Una batteria “solo grafene” già pronta in scaffale: oggi il grafene è **additivo/struttura** in catodi/anodi o elettrodo di supercap.
- Accumulo stagionale puramente elettrochimico a basso costo su scala GWh: a grande scala conviene **ibridare** LGGS (buffer elettrico) con power-to-heat o H₂. Il vault LGGS resta valido fino a decine–centinaia di kWh–MWh con KPI di autoscarica rispettati.

## 1.6 Successo del progetto

Il progetto è riuscito se, in laboratorio:

1. una cella gel-grafene sigillata sotto vuoto completa ≥ 200 cicli con RTE ≥ 88%;
2. un modulo 1–5 kWh alimenta un carico notturno tipico da PV di giorno;
3. un test di vault a 3 mesi mostra autoscarica ≤ 3%/mese a T controllata.