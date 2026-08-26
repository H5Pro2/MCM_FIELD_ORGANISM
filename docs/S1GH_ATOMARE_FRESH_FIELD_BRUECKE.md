# S1-GH: Atomare Fresh-Field-Bruecke

Stand: 2026-08-15

Status: `TECHNISCHE_OBJEKTBRUECKE_KEIN_FELDLAUF`

## Zweck

S1-GH schliesst die in S1-GG gefundene Objektluecke zwischen dem neutralen
S1-FI-Anfangsfeld und den sechs Fixed-Adapter-Aufrufen aus S1-GD.

```text
ein gebundenes neutrales S1-FI-Anfangsfeld
-> sechs tiefe Feldkopien
-> gleicher Anfangsfelddigest
-> sechs getrennte Feld- und Layerobjekte
-> je eine feste Bindung an genau einen S1-GD-Aufruf
```

## Invarianten

- Alle sechs Kopien besitzen denselben Anfangsfelddigest wie die Quelle.
- Feld-, Layer- und Dockcontainer sind von der Quelle getrennt.
- Die sechs Feld- und Layerobjekte sind auch untereinander verschieden.
- Tick null, fehlende letzte Distribution und fehlendes Substrat bleiben
  erhalten.
- Aufrufreihenfolge bleibt r2 AB/BA, r4 AB/BA, r8 AB/BA.
- Quellzustands- und Fixed-Adapter-Digests bleiben unveraendert.
- Ein Kopierfehler erzeugt kein partielles Gesamtergebnis.

## Geschlossene Grenzen

S1-GH liest keine Probeplaene und verbraucht keine Batches. Es ruft weder
Dock-Abbildung noch Neuronenprojektion noch Feldkernel auf. Beobachtete
Vektoren, Receipts, Persistenz und Claims bleiben ausgeschlossen.

Entscheidung:

```text
SIX_FRESH_FIELDS_ATOMICALLY_BOUND_REAL_KERNEL_REMAINS_CLOSED
```

## Bester naechster Schritt

S1-GI bindet den typisierten Fixed-Adapter-Realoutput und seinen reinen
Konverter in das gemeinsame S1-FX-Receipt-Schema. Die Abnahme verwendet nur
synthetisch konstruierte Rohvektoren; der reale Probe- und Feldkernel bleibt
geschlossen.
