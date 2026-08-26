# S1-GT: Statischer Sechsarm-Freigabe- und Umfangsvertrag

Stand: 2026-08-15

Status: `STATISCHER_UMFANGSVERTRAG_KEINE_FELDAUSFUEHRUNG`

## Frage

Welcher kleinste reale Anschluss ist nach S1-GS zulaessig, ohne die volle
45-Aufruf-Kette, EC46-Auswertung oder eine Memoryentscheidung zu oeffnen?

## Gebundener Umfang

Zulaessig ist nur eine begrenzte Fixed-Adapter-Sechsarmprobe:

```text
r2 AB Fixed Adapter     200 Batches
r2 BA Fixed Adapter     200 Batches
r4 AB Fixed Adapter     400 Batches
r4 BA Fixed Adapter     400 Batches
r8 AB Fixed Adapter     800 Batches
r8 BA Fixed Adapter     800 Batches
gesamt                2.800 reale Fixed-Adapter-Transitionen
```

Die Quelle bleibt die bestehende S1-GH/S1-GD-Bindung. Jeder Batch muss ueber
den S1-GS-Einzeltransitionadapter laufen und als S1-GQ-Envelope validiert
werden. Die sechs Ergebnisse duerfen nur atomar als sechs S1-GI-Ausgaben und
sechs Common-Probe-Receipts zurueckgegeben werden.

## Ausgeschlossen

Ausdruecklich nicht geoeffnet sind:

- Formation;
- P0-Probe;
- aktive Frozen-E1-Probe;
- Rueckwirkungsablation;
- Formationsablation;
- EC46- oder Fixed-Adapter-Gesamtentscheidung;
- 45-Aufruf-Same-Session-Kette;
- Writer, Persistenz, Retry oder nachtraegliche Parameterkorrektur;
- Memory-, Feldzeit-, Organisations- oder KI-Claim.

## Gate

Die S1-GO-Synthetic-only-Referenz bleibt geschlossen. S1-GT erlaubt als
naechsten Schritt nur die Implementierung eines begrenzten Sechsarm-Adapters,
nicht dessen reale Ausfuehrung.

Entscheidung:

```text
SIX_ARM_FIXED_ADAPTER_RELEASE_SCOPE_BOUND_STATIC_EXECUTION_CLOSED
```

## Bester naechster Schritt

S1-GU sollte den begrenzten Sechsarm-Adapter hinter diesem Vertrag
implementieren und nur mit injizierten zaehlenden Transitionen abnehmen:
sechs Arme, 2.800 Batchaufrufe, 660 Supports, atomare Rueckgabe, kein realer
Feldkernel.
