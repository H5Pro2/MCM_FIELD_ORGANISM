# S1-GS: Realer Einzelbatch-Transitionadapter

Stand: 2026-08-15

Status: `EINZELNER_REALTRANSITION_ADAPTER_WRAPPER_GATE_GESCHLOSSEN`

## Umsetzung

S1-GS implementiert den kleinsten projektinternen Anschluss hinter S1-GR:

```text
Fresh Binding
+ naechster Probe-Batch
+ expliziter S1-GN-Live-Field-Carrier
-> Batch-zu-Dock-Abbildung
-> lokale Neuroneneingaben
-> Fixed-Adapter-Feldkernel
-> naechster Live-Field-Carrier
-> S1-GQ-Realtransition
-> S1-GQ-Envelope
```

Der Adapter fuehrt genau einen realen Feldschritt aus. Er oeffnet den
S1-GO-Sechsarmwrapper nicht; dessen Synthetic-only-Gate bleibt unveraendert
geschlossen und weist den Real-Envelope weiterhin zurueck.

## Abnahme

- genau ein Fixed-Adapter-Feldschritt;
- `real-field-advance` im gemeinsamen S1-GQ-Envelope;
- neues `SharedMCMField`-Objekt und neuer Felddigest;
- Quellzustand und Fixed Adapter bleiben digestgleich;
- keine Persistenz, kein Writer, kein Retry;
- keine Claims und kein Memorybefund;
- S1-GO lehnt denselben Realtransition-Adapter weiterhin fail-closed ab.

Entscheidung:

```text
REAL_SINGLE_BATCH_TRANSITION_VALIDATED_WRAPPER_GATE_REMAINS_CLOSED
```

## Einordnung

S1-GS schliesst eine technische Anschlussluecke der Fixed-Adapter-Messkette.
Es ist noch keine vollstaendige Sechsarm- oder Dreissig-Probe-Ausfuehrung und
keine Bewertung gegen EC46 oder Fixed-Adapter-Erklaerung.

## Bester naechster Schritt

S1-GT sollte nur einen statischen Freigabe- und Umfangsvertrag fuer eine
begrenzte reale Fixed-Adapter-Sechsarmprobe binden: sechs Fixed-Adapter-Arme,
2800 Feldschritte, atomare Ergebnisgrenze, unveraenderte Synthetic-only-
Referenz und weiterhin keine gemeinsame 45-Aufruf-Gesamtkette.
