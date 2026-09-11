# Scheda tecnica modulo LGGS (target)

| Voce | Daily Rack | Seasonal Vault |
|---|---|---|
| Chimica | G-LFP gel | G-LFP gel (stessa cella) |
| Packaging | pouch vacuum ≤10 mbar | pouch + cabinet climatizzato |
| Tensione stringa | 48 V o 400 V | 400–800 V DC |
| Capacità modulo base | 5 kWh | 5–15 kWh |
| Corrente tipica | 0,5C | C/10–C/5 |
| DoD operativo | 80% | 70% (deposito a 50–70% SOC) |
| T operativa | −10…+45 °C | deposito 15–20 °C |
| Comunicazione | CAN / Modbus | CAN / Modbus + pressure/T |
| Protezioni | BMS OVP/UVP/OTP/OCP | idem + HVAC + EPO |
| Vita ciclo | ≥5000 @80% DoD (target) | ≥2000 + vita calendario 6 mesi |
| Autoscarica | ≤3%/mese | ≤1%/mese (target vault) |

## Stack consigliato 48 V (esempio)

- 15s N-parallel pouch 3,2 V / 10 Ah
- Per 5 kWh ≈ 10–11 stringhe in parallelo (dipende da capacità reale)
- Fuse per stringa + contattore modulo
- Slave BMS per stringa, master per rack

## Interfaccia EMS

Registri minimi: SOC, SOH, V, I, T_max, T_min, alarm_bits, pressure_flag, mode (daily|vault).
