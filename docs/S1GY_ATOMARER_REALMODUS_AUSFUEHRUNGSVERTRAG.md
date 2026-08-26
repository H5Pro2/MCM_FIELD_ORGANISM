# S1-GY: Atomarer Realmodus-Ausfuehrungsvertrag

Stand: 2026-08-15

Status: `AUSFUEHRUNGSVERTRAG_GEBUNDEN_KEINE_AUSFUEHRUNG`

## Umsetzung

S1-GY formuliert den Vertrag fuer genau einen spaeteren S1-GU-Realmodusaufruf
hinter dem S1-GX-Preflight.

Der Vertrag bindet:

- S1-GX-Preflight-Digest;
- S1-GW-Gate mit S1-GS-Callable;
- dieselbe S1-GT/S1-GK/S1-GH-Quellenkette;
- sechs Arme in r2/r4/r8 AB/BA-Reihenfolge;
- exakt 2.800 Transitionen;
- exakt 660 Supports;
- keinen Retry;
- keine Parameterkorrektur nach Start;
- keine Teilrueckgabe.

## Atomare Ergebnisgrenze

Ein spaeterer Lauf duerfte nur atomar zurueckgeben:

- sechs terminale Carrier;
- sechs S1-GI-Ausgaben;
- sechs Common-Probe-Receipts;
- 2.800 Transitiondigests;
- 2.800 Envelope-Digests;
- Quellzustands- und Fixed-Adapter-Digests vor/nach dem Lauf.

EC46-Auswertung, Fixed-Adapter-Endentscheidung, Persistenz, Writer, Retry,
Claims und Memoryentscheidung bleiben ausgeschlossen.

Entscheidung:

```text
ATOMIC_REAL_MODE_EXECUTION_CONTRACT_BOUND_NO_EXECUTION
```

## Bester naechster Schritt

S1-GZ sollte nur die Implementierungsvorabnahme fuer den echten
S1-GU-Realmodusaufruf erstellen: ein schmaler Runner darf gebaut werden, aber
zunaechst nur mit einem blockierenden Dry-Run-Gate, das vor jedem S1-GS-
Callable-Aufruf abbricht. Ziel ist die Aufrufstelle zu fixieren, noch nicht
die reale Ausfuehrung.
