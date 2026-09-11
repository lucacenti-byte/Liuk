#!/usr/bin/env python3
"""
LGGS — bilancio energetico PV + daily buffer + vault stagionale.

Uso:
  python3 energy_balance.py --scenario residenziale
  python3 energy_balance.py --scenario stagionale --pv-kwp 50 --consumo-annuo-kwh 45000
  python3 energy_balance.py --scenario custom --pv-kwp 12 --consumo-annuo-kwh 8000 --vault-mesi 5
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "irraggiamento_it_sample.csv"
MESI = [
    "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
    "Lug", "Ago", "Set", "Ott", "Nov", "Dic",
]


@dataclass
class Params:
    pv_kwp: float
    consumo_annuo_kwh: float
    frazione_notturna: float
    ore_autonomia_daily: float
    vault_mesi: int
    rte: float
    dod_daily: float
    dod_vault: float
    autoscarica_mese: float
    k_sicurezza: float
    eta_sistema_pv: float


def load_yield() -> List[float]:
    rows: List[float] = []
    with DATA_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(float(row["kwh_per_kwp"]))
    if len(rows) != 12:
        raise RuntimeError(f"Attesi 12 mesi in {DATA_PATH}, trovati {len(rows)}")
    return rows


def consumo_mensile(annuo: float) -> List[float]:
    # Profilo residenziale IT semplificato: inverno più alto
    pesi = [1.15, 1.10, 1.00, 0.95, 0.90, 0.85, 0.85, 0.90, 0.95, 1.00, 1.10, 1.25]
    s = sum(pesi)
    return [annuo * p / s for p in pesi]


def sizing_daily(p: Params) -> float:
    # Energia notturna media giornaliera
    e_notte_giorno = (p.consumo_annuo_kwh * p.frazione_notturna) / 365.0
    # Autonomia richiesta in frazione di giorno (es. 18h → 0.75)
    f_autonomia = min(p.ore_autonomia_daily / 24.0, 1.0)
    e_richiesta = e_notte_giorno * (f_autonomia / max(p.frazione_notturna, 1e-6))
    # Se ore autonomia < profilo notte, usa direttamente e_notte * ore/12 circa:
    e_target = (p.consumo_annuo_kwh / 365.0) * (p.ore_autonomia_daily / 24.0)
    e = max(e_notte_giorno, e_target)
    return p.k_sicurezza * e / (p.rte * p.dod_daily)


def bilancio_mensile(p: Params, yield_m: List[float]) -> Tuple[List[float], List[float], List[float]]:
    cons = consumo_mensile(p.consumo_annuo_kwh)
    prod = [p.pv_kwp * y * p.eta_sistema_pv for y in yield_m]
    netto = [pr - c for pr, c in zip(prod, cons)]
    return prod, cons, netto


def _nameplate(energia_utile: float, p: Params, mesi_giacenza: float) -> float:
    if energia_utile <= 0:
        return 0.0
    fattore_auto = (1.0 - p.autoscarica_mese) ** max(mesi_giacenza, 0.0)
    if fattore_auto <= 0:
        return float("inf")
    return p.k_sicurezza * energia_utile / (p.rte * p.dod_vault * fattore_auto)


def sizing_vault(p: Params, netto: List[float]) -> Tuple[float, float, float, float, float, str]:
    surplus = sum(x for x in netto if x > 0)
    deficit = -sum(x for x in netto if x < 0)

    # Energia da conservare: min tra deficit invernale e surplus estivo
    e_stagione = min(surplus, deficit)

    # Limita ai mesi di vault (usa i mesi a maggior deficit tipicamente Nov-Feb)
    deficit_mesi = sorted([(i, -netto[i]) for i in range(12) if netto[i] < 0], key=lambda t: -t[1])
    deficit_limitato = sum(v for _, v in deficit_mesi[: max(p.vault_mesi, 0)])
    e_obiettivo = min(e_stagione, deficit_limitato) if p.vault_mesi > 0 else 0.0

    e_vault = _nameplate(e_obiettivo, p, float(max(p.vault_mesi, 1)))

    # Vault pragmatico: 21 giorni del peggior mese in deficit (buffer settimane, non tutta la stagione)
    if deficit_mesi:
        peggior_mese = deficit_mesi[0][1]
        e_pratica_utile = peggior_mese * (21.0 / 30.0)
    else:
        e_pratica_utile = 0.0
    e_vault_pratico = _nameplate(e_pratica_utile, p, mesi_giacenza=1.5)

    nota = ""
    if deficit > surplus:
        nota = (
            "Il deficit invernale supera il surplus estivo: il vault 'pieno' copre solo "
            f"{surplus:.0f} kWh di fabbisogno stagionale su {deficit:.0f} kWh di deficit. "
            "Valutare più PV, riduzione consumi o ibridazione (termico/H2)."
        )
    elif e_vault > 200:
        nota = (
            f"Vault stagionale pieno da {e_vault:.0f} kWh (nameplate) è oneroso. "
            f"Raccomandato partire dal vault pragmatico (~21 giorni): {e_vault_pratico:.0f} kWh, "
            "e ibridare oltre quella scala."
        )
    return e_vault, e_vault_pratico, e_obiettivo, surplus, deficit, nota


def stampa_report(p: Params, scenario: str) -> None:
    yield_m = load_yield()
    prod, cons, netto = bilancio_mensile(p, yield_m)
    e_daily = sizing_daily(p)
    e_vault, e_vault_pratico, e_obiettivo, surplus, deficit, nota = sizing_vault(p, netto)

    print("=" * 64)
    print(f"LGGS — dimensionamento scenario: {scenario}")
    print("=" * 64)
    print(f"PV:                 {p.pv_kwp:.1f} kWp")
    print(f"Consumo annuo:      {p.consumo_annuo_kwh:.0f} kWh")
    print(f"Produzione annua:   {sum(prod):.0f} kWh (η sistema {p.eta_sistema_pv:.2f})")
    print(f"Surplus annuo:      {surplus:.0f} kWh")
    print(f"Deficit annuo:      {deficit:.0f} kWh")
    print("-" * 64)
    print(f"Daily buffer:       {e_daily:.1f} kWh  (DoD {p.dod_daily:.0%}, RTE {p.rte:.0%})")
    print(
        f"Vault pieno:        {e_vault:.1f} kWh nameplate  "
        f"(utile ~{e_obiettivo:.0f} kWh, mesi={p.vault_mesi}, autoscarica {p.autoscarica_mese:.1%}/mese)"
    )
    print(
        f"Vault pragmatico:   {e_vault_pratico:.1f} kWh nameplate  "
        f"(~21 giorni del peggior mese in deficit)"
    )
    print("-" * 64)
    print(f"{'Mese':<6}{'PV':>10}{'Consumo':>10}{'Netto':>10}")
    for i, nome in enumerate(MESI):
        print(f"{nome:<6}{prod[i]:10.0f}{cons[i]:10.0f}{netto[i]:10.0f}")
    print("-" * 64)
    if nota:
        print("AVVISO:", nota)
    else:
        print("OK: surplus estivo sufficiente a coprire il deficit considerato dal vault.")
    print()
    print("Nota: valori orientativi per design; validare con dati sito e profilo reale.")


def build_params(args: argparse.Namespace) -> Tuple[Params, str]:
    if args.scenario == "residenziale":
        p = Params(
            pv_kwp=args.pv_kwp or 6.0,
            consumo_annuo_kwh=args.consumo_annuo_kwh or 4000.0,
            frazione_notturna=0.35,
            ore_autonomia_daily=args.ore_autonomia_daily or 14.0,
            vault_mesi=args.vault_mesi if args.vault_mesi is not None else 3,
            rte=0.90,
            dod_daily=0.80,
            dod_vault=0.70,
            autoscarica_mese=0.01,
            k_sicurezza=1.15,
            eta_sistema_pv=0.85,
        )
        return p, "residenziale"
    if args.scenario == "stagionale":
        p = Params(
            pv_kwp=args.pv_kwp or 50.0,
            consumo_annuo_kwh=args.consumo_annuo_kwh or 45000.0,
            frazione_notturna=0.30,
            ore_autonomia_daily=args.ore_autonomia_daily or 16.0,
            vault_mesi=args.vault_mesi if args.vault_mesi is not None else 4,
            rte=0.90,
            dod_daily=0.80,
            dod_vault=0.70,
            autoscarica_mese=0.01,
            k_sicurezza=1.20,
            eta_sistema_pv=0.85,
        )
        return p, "stagionale"
    # custom
    p = Params(
        pv_kwp=args.pv_kwp or 12.0,
        consumo_annuo_kwh=args.consumo_annuo_kwh or 8000.0,
        frazione_notturna=args.frazione_notturna or 0.33,
        ore_autonomia_daily=args.ore_autonomia_daily or 14.0,
        vault_mesi=args.vault_mesi if args.vault_mesi is not None else 4,
        rte=args.rte or 0.90,
        dod_daily=0.80,
        dod_vault=0.70,
        autoscarica_mese=args.autoscarica_mese or 0.01,
        k_sicurezza=1.15,
        eta_sistema_pv=0.85,
    )
    return p, "custom"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Dimensionamento LGGS PV + gel-grafene")
    ap.add_argument(
        "--scenario",
        choices=["residenziale", "stagionale", "custom"],
        default="residenziale",
    )
    ap.add_argument("--pv-kwp", type=float, default=None)
    ap.add_argument("--consumo-annuo-kwh", type=float, default=None)
    ap.add_argument("--ore-autonomia-daily", type=float, default=None)
    ap.add_argument("--vault-mesi", type=int, default=None)
    ap.add_argument("--frazione-notturna", type=float, default=None)
    ap.add_argument("--rte", type=float, default=None)
    ap.add_argument("--autoscarica-mese", type=float, default=None)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    params, name = build_params(args)
    stampa_report(params, name)


if __name__ == "__main__":
    main()
