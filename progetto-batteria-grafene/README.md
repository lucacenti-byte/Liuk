# LGGS — Liuk Graphene Gel Storage

Sistema di accumulo elettrochimico a **elettrodi di grafene in elettrolita gel**, sigillato sotto vuoto, per impianti fotovoltaici.

Obiettivi d’uso:

1. **Notturno** — buffer giornaliero (carica di giorno → scarica di notte)
2. **Stagionale** — eccedenza estiva conservata per l’inverno (moduli a bassissima autoscarica + vault termocontrollato)
3. **Grande scala** — architettura modulare a rack, parallelizzabile fino a MWh

> Stato: dossier di progetto R&D (TRL 2→4). Non è un prodotto commerciale: definisce chimica target, packaging, integrazione PV, dimensionamento e roadmap di laboratorio.

## Struttura

| Percorso | Contenuto |
|---|---|
| [`docs/01-visione-e-obiettivi.md`](docs/01-visione-e-obiettivi.md) | Problema, requisiti, KPI |
| [`docs/02-architettura-sistema.md`](docs/02-architettura-sistema.md) | PV ↔ inverter ↔ LGGS ↔ carichi |
| [`docs/03-cella-gel-vuoto.md`](docs/03-cella-gel-vuoto.md) | Cella, gel, packaging sotto vuoto |
| [`docs/04-dimensionamento.md`](docs/04-dimensionamento.md) | Metodo sizing giorno/notte e stagione |
| [`docs/05-roadmap-trl.md`](docs/05-roadmap-trl.md) | Fasi, BOM lab, costi ordine di grandezza |
| [`docs/06-sicurezza-normativa.md`](docs/06-sicurezza-normativa.md) | Sicurezza, norme, rischi |
| [`docs/07-scheda-modulo.md`](docs/07-scheda-modulo.md) | Scheda tecnica modulo daily/vault |
| [`docs/08-protocollo-lab-f2.md`](docs/08-protocollo-lab-f2.md) | Protocollo prima cella da laboratorio |
| [`sim/energy_balance.py`](sim/energy_balance.py) | Simulatore bilancio energetico |
| [`schematics/sistema.mmd`](schematics/sistema.mmd) | Schema a blocchi (Mermaid) |

## Avvio rapido simulazione

```bash
cd progetto-batteria-grafene/sim
python3 energy_balance.py --scenario residenziale
python3 energy_balance.py --scenario stagionale --pv-kwp 50 --consumo-annuo-kwh 45000
```

## Idea chiave in una frase

Elettrodi a rete di grafene immersi in un **gel ionico** (quasi-solido), confezionati in pouch **sotto vuoto** per ridurne ossidazione e umidità: moduli adatti al ciclo notturno e, in vault dedicato, a conservazione stagionale a bassa autoscarica.