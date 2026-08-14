# S1-GF: Synthetische Fixed-Adapter-Positivstruktur

Stand: 2026-08-15

Status: `SYNTHETISCHE_STRUKTURABNAHME_KEIN_FELDLAUF`

## Zweck

S1-GF oeffnet die in S1-GE gesperrte positive Planstruktur ausschliesslich
fuer einen injizierten zaehlenden Fake-Kernel. Damit werden Reihenfolge,
Bilanz und atomarer Abbruch des spaeteren Fixed-Adapter-Wrappers geprueft,
ohne den realen Feldkernel aufzurufen.

## Gebundene Struktur

Die sechs S1-GD-Aufrufe werden unveraendert in dieser Reihenfolge verbraucht:

```text
r2 fixed-adapter-ab: 200 Batches
r2 fixed-adapter-ba: 200 Batches
r4 fixed-adapter-ab: 400 Batches
r4 fixed-adapter-ba: 400 Batches
r8 fixed-adapter-ab: 800 Batches
r8 fixed-adapter-ba: 800 Batches
```

Gesamt: 2.800 positive Batches und 2.800 bilanzierte Feldschritte.

Jeder Batch muss genau dem gleich indizierten `proposal_step` entsprechen.
Der Fake-Kernel erhaelt nur das gebundene S1-GD-Aufrufobjekt und den
typisierten Batch. Er gibt ein synthetisches Zaehl-Receipt zurueck.

## Abnahme

Die Tests belegen:

- sechs Aufrufe und alle 2.800 Batches werden genau einmal und geordnet
  verbraucht;
- r2/r4/r8 werden mit 400/800/1.600 Batches bilanziert;
- 2.800 Fake-Kernel-Aufrufe entsprechen 2.800 bilanzierten Schritten;
- tatsaechlich ausgefuehrte Feldschritte bleiben null;
- Quellzustaende und Fixed-Adapter bleiben digestgleich;
- manipulierte Gates und Receipts brechen fail-closed ab;
- ein Fehler des injizierten Kernels erzeugt kein partielles
  Gesamtergebnis;
- es werden keine Feldobjekte, Beobachtungsvektoren oder persistenten
  Ausgaben erzeugt.

## Aussagegrenze

S1-GF prueft nur die Kontrollfluss- und Bilanzstruktur. Es misst keine
Fixed-Adapter-Wirkung und liefert weder einen Substrat- noch einen Memory-,
Feldzeit-, Organisations- oder KI-Nachweis.

Entscheidung:

```text
FIXED_ADAPTER_POSITIVE_STRUCTURE_SYNTHETICALLY_VALIDATED_REAL_PATH_CLOSED
```

## Bester naechster Schritt

S1-GG bindet statisch den kleinsten realen Fixed-Adapter-Aufrufkern an die
S1-GF-Schnittstelle: notwendige Eingaben, frischer Feldzustand, Batch-zu-Dock-
Abbildung, Neuroneneingabe, Rohvektorausgabe und gemeinsames Receipt. Noch
keine Ausfuehrung und keine Einmallauffreigabe.
