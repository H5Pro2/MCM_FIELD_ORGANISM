# S2-GW: Einmaliger S2-GT-Hauptlauf

Stand: 2026-08-30

## Laufbindung

```text
Lauf-ID: s2gw-run-20260830-01
run_main_once-Aufrufe: 1
read-only Verifikatoraufrufe: 1
EvaluationPlanSeal:
1838da68fa3184a8be277b59b81bfa87332cc94f2be8f9282e91a9885ec0fb5c
```

Das Gate wurde nur im ausfuehrenden Prozess vor dem einen Aufruf geoeffnet
und im `finally`-Abschluss wieder auf `False` gesetzt. Die versionierte Quelle
blieb durchgehend bei `MAIN_EXECUTION_ENABLED = False`.

## Ergebnis

```text
NOT_EVALUABLE
```

Der Lauf stoppte bei `op-0002`, der ersten
`FORMATION_RECEPTOR_ANALYSIS`. Der unmittelbare Laufabbruch lautete:

```text
E008: registered resource limit was exceeded
```

Damit wurde kein ReceptorReceipt fuer `op-0002` publiziert. Der Runner
schloss den bereits reservierten Lauf anschliessend ueber den registrierten
Fehlerpfad `fp-0002` und die drei Fehlerabschlussoperationen. Der terminale
Fehlerbeleg verwendet dabei den generischen Runnercode `E009`.

Gespeichert wurden:

- 10 verkettete Ereignisse;
- Manifest und Reservierungsbeleg;
- `RunFailureReceipt`;
- `FailureTerminalFinding`;
- der exklusive Marker `terminal/failure/NOT_EVALUABLE`.

Es entstanden kein ExecutionEvidencePackage, keine EvaluationRunBinding,
keine Funktionsauswertung und kein `COMPLETE`-Marker.

## Unabhaengige Verifikation

Die genau einmal aufgerufene read-only Verifikation ergab ebenfalls:

```text
verification_status: NOT_EVALUABLE
operation_count: 0
event_count: 10
recorded_bytes: 8665
```

Der Verifikator meldete erwartungsgemaess das fehlende Erfolgsartefakt fuer
`op-0002`. Dies aendert den bereits terminalen Fehlerstatus nicht.

## Quellidentitaet

| Modul | SHA-256 vorher und nachher |
| --- | --- |
| `_s2gt_private_fixture_registry.py` | `5d4ed450c2443f51839acfb9717661b8c54422be3fd87605c50b020e5a887849` |
| `_s2gt_private_runner.py` | `d166a488fc56eca69b2b161f75d2503148e4319c854a285fe090020da6f25a77` |
| `_s2gt_private_append_only_recorder.py` | `8c418e31afa76348cb92f2971ab24f63c0a5a12c67401cc842bea8f5b58a5172` |
| `_s2gt_private_result_verifier.py` | `5c5884d7eec9e4a3262f951af8e61da7b074bea521c2f7c83052612297f0b2d6` |

Alle vier Werte waren vor und nach dem Lauf identisch.

## Fachliche Grenze

S2-GW liefert keinen positiven oder negativen Befund zur Kontextverwendung.
Die sieben gebundenen Faelle wurden nicht erreicht und duerfen nicht aus
Zwischenwerten interpretiert werden. Der Lauf wird weder fortgesetzt noch
wiederholt oder nachtraeglich repariert.

## Naechster Schritt

Vor jeder neuen Laufentscheidung ist ein enger statischer Ursachen- und
Budgetaudit fuer die konkrete Serialisierung des `op-0002`-ReceptorReceipts
erforderlich. Dabei sind die tatsaechliche neutrale Receiptgroesse, die
registrierte 4.096-Byte-Grenze und die Abbildung des unmittelbaren Fehlers
`E008` auf den terminalen Fehlercode getrennt zu pruefen. Eine erneute
Ausfuehrung ist damit nicht freigegeben.

