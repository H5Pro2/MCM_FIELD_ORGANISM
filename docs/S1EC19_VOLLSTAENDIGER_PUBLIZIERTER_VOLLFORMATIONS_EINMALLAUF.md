# S1-EC19: Vollstaendiger publizierter Vollformations-Einmallauf

## Status

```text
FULL_FORMATION_EXECUTED_ONCE
FIFTEEN_STATES_PUBLISHED
TWO_THOUSAND_ONE_HUNDRED_SEVENTY_FIVE_BINDINGS_PUBLISHED
FINAL_REREAD_VERIFIED
TYPED_RELOAD_VERIFIED
ATTEMPT_REMOVED_AFTER_VERIFICATION
LOCK_RELEASED
NO_PROBE
NO_CLAIMS
```

S1-EC19 fuehrte nach der statischen S1-EC18-Freigabe genau eine neue
15-armige `r2/r4/r8`-Vollformation aus. Anders als S1-EC13 publiziert der
Bericht nicht nur einen Ergebnisdigest, sondern den vollstaendigen
S1-EC14-Handoff mit allen gebildeten E1-Zustaenden.

## Implementierung

```text
mcm_field_organism/e1_confirmation_full_published_one_shot.py
tests/test_e1_confirmation_full_published_one_shot.py
```

Der bestehende Formationsconsumer akzeptiert dafuer einen expliziten
Aggregate-Attempt und einen Laufzeitwaechter. Die historischen S1-EC3- und
S1-EC13-Pfade werden nicht als Marker oder Bericht verwendet.

## Einmallauf

```text
execution_id = e1.full-formation-published-run.s1ec19.once.v1
runtime_seconds = 365.323444099864
report_bytes = 301732
report_sha256 = 93cc94ddb18f80919067ff4e29ccae5aa038bb436d72584acef2d38e57be1fcc
formation_result_digest = 738e76210eeaa73d3a614eea461de1178ac5f4500f6b9e107cf8f8a8d193ee48
handoff_payload_digest = ab4adb41160675d93d67e3454021430bb4482131b22ec752bb3110ae5983a2c6
state_count = 15
edge_binding_count = 2175
```

Die unmittelbar vor dem Lauf erneut gemessenen Ressourcen waren:

```text
free_memory_bytes = 7737597952
free_disk_bytes = 236813230080
resource_snapshot_digest = 3fad16ef540f4fffac838d6140f36cf754d8add1d6139075c0c520850277ffbb
release_decision_digest = 94b10a3596160ce0e9538db2d5de47ef745e04e62cf508306a199147b78e7660
```

## Rohwerte

```text
AB/BA-Zustandsabstand:
r2 = 0.0008453023645430579
r4 = 0.000852954804258883
r8 = 0.0008568014728262579

Verfeinerungsrest:
r2 -> r4 = 3.4885390053043374e-05
r4 -> r8 = 1.736313599644745e-05

convergence_nonincreasing = true
all_five_arm_controls_passed = true
prepared_inputs_preserved = true
```

Diese Werte reproduzieren die S1-EC13-Vollformation exakt. Der neue
technische Fortschritt ist die vollstaendige, digestgebundene Persistierung
und Rekonstruktion der 15 Zustandsarme, nicht ein neuer numerischer Effekt.

## Artefakt

```text
synthetic_runs/s1ec19_full_published_once_v1/
  e1_full_formation_published_s1ec19_once_v1.json
```

Der finale Bericht besteht. Attempt und Lock sind abwesend. Die Identitaet
darf nicht erneut ausgefuehrt werden.

## Evidenzgrenze

S1-EC19 weist nach, dass die zeitgeordnet gebildeten E1-Zustaende in einem
kontrollierten Vollformationslauf vollstaendig erhalten, atomar publiziert
und typisiert rekonstruiert werden koennen. Es wurde keine spaetere Probe
ausgefuehrt. Daher liegt weiterhin kein Nachweis fuer Memory, Rekonstruktion,
Organisation, Semantik, Selbstregulation oder KI vor.

## Bester naechster Schritt

S1-EC20 sollte den persistierten Bericht ausschliesslich statisch auf einen
spaeteren Probe-Handoff pruefen: Schutzhash binden, alle 15 Rollen und 2.175
Bindungen erneut inventarisieren, die zulassigen Probe-Kandidaten bestimmen
und eine identische frische Probe samt Ablation und fester Adapterbaseline
vorregistrieren. Noch keine Probe ausfuehren.
