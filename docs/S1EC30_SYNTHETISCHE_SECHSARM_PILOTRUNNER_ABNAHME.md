# S1-EC30: Synthetische Sechsarm-Pilotrunner-Abnahme

## Status

```text
SIX_BATCHES_ORCHESTRATED
THIRTY_SIX_SYNTHETIC_ARM_RECEIPTS_COMPLETE
P0_ABLATION_AND_ACTIVE_ROLES_SEPARATE
FAIL_FAST_AND_RECEIPT_ALIGNMENT_VERIFIED
ZERO_FIELD_STEPS_EXECUTED
NO_PERSISTENCE_DECISION_OR_CLAIM
```

S1-EC30 implementiert die Orchestrierung des in EC29 gebundenen n1/n2-
Piloten. Die Abnahme verwendet ausschliesslich typisierte synthetische
Receipts. Der Einstieg akzeptiert keine realen Feldresultate und kann die
EC29-Ausfuehrungssperre nicht ueberschreiten.

## Abnahme

```text
EC29 contract digest = 834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8
EC30 raw result digest = 700b0296be5cc04ac5049a447d0c6feb9f6b6ec50eb19915fc235c0c2fd697c0

batches completed = 6
arm calls = 36
P0 receipts = 12
formation-ablation receipts = 12
active-E1 receipts = 12
planned field-arm steps = 25,368
executed field steps = 0
```

Die Reihenfolge ist exakt n1-r2/r4/r8 vor n2-r2/r4/r8. Innerhalb jedes
Batches folgen P0, Bildungsablation und Aktivarme in der EC29-Reihenfolge.

## Fehlergrenzen

- Ein Kernelabbruch beim vierten Aufruf stoppt exakt dort.
- Es wird kein partieller Rohcontainer zurueckgegeben.
- Ein Receipt mit falscher Batch-, Kontakt-, Refinement- oder Armrolle wird
  sofort verworfen.
- Jedes synthetische Receipt erzwingt `field_steps_executed = 0`.
- Es existiert kein Writer-, Marker-, Entscheidungs- oder Claimpfad.

## Evidenzgrenze

S1-EC30 bestaetigt nur Orchestrierungs-, Reihenfolge- und Fehlerverhalten.
Es wurden keine P0-, Ablations- oder Aktivfelder ausgefuehrt. Es gibt keinen
Befund zu wiederholungsabhaengiger Bildung, Praegung, Memory oder KI.

## Bester naechster Schritt

S1-EC31 sollte einen rein statischen Real-Preflight binden: aktuelle freie
Ressourcen, unveraenderte EC27-/EC29-Digests, Real-Kernel-Rollenadapter,
Runtimegrenze, in-memory Rohcontainer und ausdrueckliche Eigentuemerfreigabe.
Erst dieser Preflight darf entscheiden, ob der nichtkanonische n1/n2-Pilot
einmal ausgefuehrt werden darf. Noch keine Ausfuehrung.
