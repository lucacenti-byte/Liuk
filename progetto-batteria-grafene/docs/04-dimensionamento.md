# 4. Dimensionamento

## 4.1 Principio

Due accumulatori logici (anche stessa chimica, policy diverse):

\[
E_{\mathrm{daily}} = \frac{E_{\mathrm{notte}}}{\eta_{\mathrm{RTE}} \cdot \mathrm{DoD}} \cdot k_{\mathrm{sicurezza}}
\]

\[
E_{\mathrm{vault}} = \frac{E_{\mathrm{deficit\ invernale}}}{\eta_{\mathrm{RTE}} \cdot \mathrm{DoD_{\mathrm{stag}}} \cdot (1 - d)^{m}} \cdot k_{\mathrm{sicurezza}}
\]

dove \(d\) è l’autoscarica mensile e \(m\) i mesi di deposito.

## 4.2 Input tipici

| Parametro | Default residenziale | Default stagionale PMI |
|---|---|---|
| PV | 6 kWp | 50 kWp |
| Consumo annuo | 4 000 kWh | 45 000 kWh |
| Frazione notturna del consumo | 0,35 | 0,30 |
| Ore autonomia daily | 12–24 h | 12–24 h |
| Mesi vault | 4 | 4 |
| RTE | 0,90 | 0,90 |
| DoD daily / vault | 0,80 / 0,70 | 0,80 / 0,70 |
| Autoscarica | 0,01 /mese | 0,01 /mese |
| k sicurezza | 1,15 | 1,20 |

## 4.3 Metodo giornaliero (notte)

1. Stimare energia consumata dalla sera all’alba \(E_{\mathrm{notte}}\)
2. Correggere per RTE e DoD
3. Verificare che il PV medio giornaliero estivo/invernale possa ricaricare il daily oltre al carico diurno

Regola pratica residenziale IT:

- 6 kWp → daily **10–15 kWh** copre bene la notte
- Sotto-dimensionare (5 kWh) riduce costi ma aumenta prelievo rete

## 4.4 Metodo stagionale

1. Bilancio mensile: produzione PV stimata − consumo
2. Sommare i surplus estivi e i deficit invernali
3. \(E_{\mathrm{vault}}\) ≈ deficit invernale accumulabile (limitato dal surplus estivo disponibile dopo daily + export policy)
4. Correggere per autoscarica sui mesi di giacenza

**Realtà ingegneristica:** per molti siti IT il deficit invernale di una casa è dell’ordine di **centinaia di kWh–1 MWh**. Un vault elettrochimico da 1 MWh è tecnicamente possibile ma costoso; conviene:

- ridurre fabbisogno (efficienza, pompa di calore dimensionata, ecc.),
- usare vault LGGS per **settimane–2–3 mesi** di backup strategico,
- oltre quella scala, ibridare con termico / H₂.

Il simulatore rende esplicito questo trade-off.

## 4.5 Irraggiamento semplificato

Il file [`../data/irraggiamento_it_sample.csv`](../data/irraggiamento_it_sample.csv) fornisce kWh/kWp/mese tipici Italia centro (orientativo). Produzione:

\[
E_{\mathrm{PV},m} = P_{\mathrm{kWp}} \cdot Y_m \cdot \eta_{\mathrm{sistema}}
\]

con \(\eta_{\mathrm{sistema}} \approx 0,85\) (sporcizia, cavi, inverter).

## 4.6 Tool

```bash
python3 sim/energy_balance.py --scenario residenziale
python3 sim/energy_balance.py --scenario stagionale --pv-kwp 50 --consumo-annuo-kwh 45000
python3 sim/energy_balance.py --scenario custom --pv-kwp 12 --consumo-annuo-kwh 8000 --vault-mesi 5
```

Output: sizing daily/vault, bilancio mensile, avvisi se il vault richiesto supera il surplus estivo.

## 4.7 Criteri di accettazione sizing

- Daily ricaricabile in ≥ 90% dei giorni sereni medi mensili
- Vault ≤ min(surplus estivo netto, deficit invernale corretto)
- Costo ordine di grandezza dichiarato in roadmap (non vincolo soft di accettazione lab)