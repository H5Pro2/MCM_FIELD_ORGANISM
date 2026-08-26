# S1-GW: Realmodus-Gate fuer S1-GU

Stand: 2026-08-15

Status: `REALMODUS_GATE_GEBUNDEN_KEINE_AUSFUEHRUNG`

## Umsetzung

S1-GW ergaenzt einen expliziten Gate fuer den S1-GU-Realmodus:

```text
S1-GV Realmodusvertrag
-> S1-GW Gate
-> S1-GS Transition-Callable fuer spaetere S1-GU-Injektion
```

Der Gate akzeptiert nur einen typisierten S1-GV-Vertrag. Die ausgewaehlte
Transition ist ausschliesslich `advance_e1_formation_s1gs_real_single_batch_transition`.
Der Gate ruft diese Transition nicht auf.

## Grenze

Gebunden bleiben:

- sechs Fixed-Adapter-Arme;
- 2.800 geplante reale Transitionen;
- 2.800 geplante Feldschritte;
- 660 Supports;
- keine Besitzerautorisierung;
- keine Feldexecution;
- keine Formation, P0, Frozen-E1-Probe oder Ablation;
- keine 45-Aufruf-Kette;
- keine Persistenz, kein Writer, kein Retry;
- kein Memoryclaim.

Entscheidung:

```text
S1GU_REAL_MODE_GATE_BOUND_EXECUTION_STILL_CLOSED
```

## Bester naechster Schritt

S1-GX sollte den S1-GU-Adapter mit dem S1-GW-Gate in einem synthetischen
Realmodus-Preflight verbinden: Der Preflight darf nur pruefen, dass S1-GW den
S1-GS-Callable liefert und dass ein spaeterer Lauf exakt sechs Arme und 2.800
Transitionen erwarten wuerde. Der Callable wird dabei nicht ausgefuehrt.
