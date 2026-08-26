# S1-GQ: Real-Transition-Schema und gemeinsamer Envelope

Stand: 2026-08-15

Status: `TYPEN_IMPLEMENTIERT_KEIN_REALADAPTER_KEINE_AUSFUEHRUNG`

## Umsetzung

S1-GQ trennt die beiden Carrier-Transitionen typseitig:

```text
Synthetische S1-GN-Transition
  gleiches Feldobjekt, gleicher Felddigest, 0 reale Schritte

Reales S1-GQ-Transition-Schema
  neues Feldobjekt, neuer Felddigest, exakt 1 realer Schritt
```

Beide besitzen nur einen schmalen gemeinsamen Envelope fuer Route, Batchzeit,
Supportbilanz, Feldobjektwechsel, Schrittbilanz und geschlossene
Persistenz-/Claim-Grenzen. Der Envelope kopiert und veraendert kein Feld.

## Geschlossene Grenze

Das Real-Transition-Schema besitzt absichtlich keinen Builder. Das Modul
importiert weder Batch-Mapper, Neuronenprojektor noch Feldkernel und kann daher
keine reale Transition erzeugen oder ausfuehren. Praktisch abgenommen wurde
nur die bestehende synthetische S1-GN-Transition durch den gemeinsamen
Envelope.

Entscheidung:

```text
SEPARATE_REAL_TRANSITION_SCHEMA_AND_SHARED_ENVELOPE_READY
```

Dies ist eine technische Typgrundlage, kein Feld-, Substrat- oder
Memory-Befund.

## Bester naechster Schritt

S1-GR stellt den privaten S1-GO-Wrapper auf den gemeinsamen S1-GQ-Envelope um
und nimmt seine sechs synthetischen Arme erneut ab. Der reale Transitionstyp
wird dabei weiterhin nicht erzeugt und der Feldkernel bleibt geschlossen.
