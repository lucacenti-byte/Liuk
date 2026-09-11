# 6. Sicurezza e normativa

## 6.1 Principi

Anche con gel e LFP (chimica relativamente stabile) restano rischi termici, elettrici e chimici. Il vuoto **non** elimina il rischio di thermal runaway: riduce ossidanti e umidità, ma l’energia chimica resta nella cella.

## 6.2 Controlli di progetto

- Preferenza **LFP + grafene** (no NMC alto Ni in vault stagionale)
- DoD e SOC vault limitati (50–70% in deposito)
- BMS con OVP/UVP/OTP/OCP, bilanciamento, contattori
- Cabinet con rilevazione fumo/temperatura, ventilazione, EPO
- Separazione fisica daily rack / vault
- Procedure di formazione e degassing in area controllata

## 6.3 Manipolazione lab

- Materiali litio-ionici e solventi: DPI, schede SDS
- Dry room / glovebox per umidità
- Divieto di forare pouch sotto tensione
- Smaltimento elettroliti e scrap secondo rifiuti pericolosi

## 6.4 Norme di riferimento (obiettivo conformità)

| Ambito | Norma / quadro |
|---|---|
| Batterie stazionarie | IEC 62619, IEC 63056 |
| Installazione | IEC 60364, CEI 64-8 (IT) |
| EMC | IEC 61000 serie |
| Trasporto prototipi | UN 38.3 |
| Marcatura / mercato EU | Battery Regulation (EU) 2023/1542 (roadmap) |

## 6.5 Rischi di progetto

| Rischio | Impatto | Mitigazione |
|---|---|---|
| Autoscarica &gt; target | vault inutile | gel, vacuum, T, SOC |
| Costo GNP | economics | GNP industriale, loading ottimizzato |
| Gassing pouch | swelling / leak | degas 2°, additivi, LFP |
| Complessità EMS | sottoutilizzo | regole semplici + telemetria |
| Overpromise stagionale | delusione stakeholder | sizing onesto + ibrido P2X |

## 6.6 Etica e claim

Comunicare sempre: prototipo R&D, non storage stagionale “illimitato”. I numeri di densità e autoscarica sono **target**, da validare sperimentalmente.