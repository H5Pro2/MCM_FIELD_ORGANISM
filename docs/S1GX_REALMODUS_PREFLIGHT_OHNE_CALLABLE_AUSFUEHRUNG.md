# S1-GX: Realmodus-Preflight ohne Callable-Ausfuehrung

Stand: 2026-08-15

Status: `PREFLIGHT_GEBUNDEN_CALLABLE_NICHT_AUSGEFUEHRT`

## Umsetzung

S1-GX verbindet die bisher getrennten Grenzen:

```text
S1-GT Umfangsvertrag
+ S1-GV Realmodusvertrag
+ S1-GW Gate
+ S1-GK Quellenvertrag
+ S1-GH Fresh Fields
-> Preflight fuer spaeteren S1-GU-Realmodus
```

Der Preflight prueft, dass S1-GW den S1-GS-Callable fuer eine spaetere
S1-GU-Injektion liefern wuerde. Der Callable wird nicht ausgefuehrt, und der
S1-GU-Runner wird nicht gestartet.

## Gebundene Erwartung

- sechs Arme;
- r2/r4/r8 AB/BA-Reihenfolge;
- 2.800 erwartete Transitionen;
- 2.800 erwartete Feldschritte;
- 660 Supports;
- sechs erwartete Outputs;
- sechs erwartete Receipts.

## Grenze

Weiterhin geschlossen bleiben Realmodusausfuehrung, Besitzerautorisierung,
Feldexecution, volle 45-Aufruf-Kette, Persistenz, Retry, Claims und
Memoryentscheidung.

Entscheidung:

```text
S1GU_REAL_MODE_PREFLIGHT_BOUND_CALLABLE_NOT_EXECUTED
```

## Bester naechster Schritt

S1-GY sollte nur einen atomaren Realmodus-Ausfuehrungsvertrag formulieren:
Vorbedingungen, ein einziger spaeterer S1-GU-Aufruf mit S1-GW-Callable,
kein Retry, keine Persistenz, keine EC46-/Memoryentscheidung und eine
geschlossene Ergebnisgrenze. Noch keine Ausfuehrung.
