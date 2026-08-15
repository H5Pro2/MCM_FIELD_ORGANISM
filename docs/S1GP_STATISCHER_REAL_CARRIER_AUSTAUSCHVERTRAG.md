# S1-GP: Statischer Real-Carrier-Austauschvertrag

Stand: 2026-08-15

Status: `STATISCHE_TYPBINDUNG_KEINE_AUSFUEHRUNG`

## Ergebnis

Der kleinste reale Austauschpunkt ist jetzt statisch gebunden:

```text
Fresh Binding + Batch + aktueller LiveFieldCarrier
-> Batch-zu-Dock-Abbildung
-> lokale Neuroneneingaben
-> leere Randdistribution fuer die exakte Batchzeit
-> Fixed-Adapter-Feldkernel
-> neues SharedMCMField
-> naechster LiveFieldCarrier
```

Der S1-GN-Carrier enthaelt bereits alle benoetigten Eingaben. Die vorhandene
reale Map-Projektions-Kernel-Kette ist signaturkompatibel.

## Gefundene Typgrenze

Die S1-GN-Transition ist absichtlich rein synthetisch. Sie verlangt:

- dasselbe Feldobjekt vor und nach der Transition;
- unveraenderten Felddigest;
- `synthetic_no_field_advance = true`;
- null tatsaechliche Feldschritte.

Zum Stand S1-GP akzeptierte S1-GO genau diesen Typ und wies Transitionen mit
realen Feldschritten zurueck. Seit S1-GR prueft der Wrapper den gemeinsamen
S1-GQ-Envelope; seine aktuelle Synthetic-only-Gate weist reale Transitionen
weiterhin zurueck. Der reale Adapter darf nicht in den synthetischen Typ
hineingezwungen werden.

Der kleinste sichere Anschluss ist ein eigener Real-Transitionstyp mit
explizitem vorherigem und naechstem Carrier, neuem Feldobjekt, neu berechnetem
Felddigest und exakt um eins erhoehter Schritt-, Batch- und Supportbilanz.

Entscheidung:

```text
REAL_EXCHANGE_POINT_BOUND_SEPARATE_REAL_TRANSITION_TYPE_REQUIRED
```

Dies ist eine technische Typenkorrektur, keine wissenschaftliche Sackgasse
und kein Feld-, Substrat- oder Memory-Befund. Es wurde kein Adapter oder
Feldkernel ausgefuehrt.

## Bester naechster Schritt

S1-GQ implementiert nur das separate, nicht ausfuehrende Schema fuer eine
reale Carrier-Transition und einen gemeinsamen schmalen Transitionvertrag,
den der Wrapper spaeter fuer synthetische und reale Transitionen pruefen kann.
Der reale Batch-Adapter bleibt geschlossen.
