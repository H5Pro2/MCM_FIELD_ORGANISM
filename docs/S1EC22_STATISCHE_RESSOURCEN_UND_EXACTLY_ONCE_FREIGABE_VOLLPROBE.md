# S1-EC22: Statische Ressourcen- und Exactly-once-Freigabe der Vollprobe

## Status

```text
FREIGABE
ALL_SEVENTEEN_STATIC_GATES_PASSED
EXACT_PROBE_LOAD_BOUND
NEW_S1_EC23_TARGET_PATHS_UNUSED
NO_PROBE_EXECUTION
NO_MARKERS
NO_REPORT
NO_RESULT_DECISION
NO_CLAIMS
```

S1-EC22 bindet die Ressourcen- und Exactly-once-Grenze fuer eine spaetere
einmalige Probe der persistenten S1-EC19-Zustaende. Die Pruefung liest nur
Vertraege, Plaene, Digests, Pfadzustaende und Systemressourcen. Sie erzeugt
keine Probefelder und fuehrt keinen Feldschritt aus.

## Implementierung

```text
mcm_field_organism/e1_confirmation_full_probe_release_audit.py
tests/test_e1_confirmation_full_probe_release_audit.py
```

## Korrigierte Lastinventur

Die zuvor dokumentierte Schaetzung `400/800/1600` beziehungsweise 19.600
Feldarm-Schritte war zu hoch. Die typisierten, tatsaechlich gebundenen
Probeplaene enthalten:

```text
r2 = 200 Planschritte
r4 = 400 Planschritte
r8 = 800 Planschritte

proposal_step_count = 1400
probe_arm_count = 7
field_arm_step_count = 9800
source_support_count_per_plan = 110
```

Diese Zahlen werden aus den Planobjekten ermittelt und vom Vertrag exakt
geprueft. Die Korrektur veraendert weder Probequelle noch Supports,
Zeitgrenzen oder Feldoperatoren.

## Neue Identitaet und Schranken

```text
execution_id = e1.full-published-probe.s1ec23.once.v1
target = synthetic_runs/s1ec23_full_published_probe_once_v1
maximum_runtime_seconds = 1200.0
maximum_report_bytes = 4194304
minimum_free_memory_bytes = 4294967296
minimum_free_disk_bytes = 1073741824
runtime_abort_policy = abort-before-1200-seconds-retain-attempt
```

Bericht, Attempt und Lock besitzen neue Namen. Nach einem erzeugten Attempt
ist jede automatische Wiederholung gesperrt. Ein Fehler nach Attempt laesst
den Attempt als terminale Spur bestehen.

## Statische Entscheidung

Am 12. August 2026 wurden gemessen:

```text
free_memory_bytes = 7686373376
free_disk_bytes = 236811141120
policy_digest = 493df3be63768f65f636996abd68e0b6cf8c2eed39eb7bd34a62bc867f9af487
handoff_audit_digest = 3524e973ee92e0551d85ea8be561ea0006f61909d3779e1e81cdb2109f596c2a
resource_snapshot_digest = 1cad157db851612fcf95ec700442d6e396c02f7c8176b029c498623ea58f3e7e
decision_digest = e472f64d475964d4933459a0a47e7192f92aa3e50947f7ff31583bbbf8108d1b
```

Alle 17 Gates bestanden. Die Entscheidung lautet `FREIGABE` fuer die
Vorbereitung von S1-EC23. Innerhalb von S1-EC22 bleiben geschlossen:

```text
probe_execution_authorized = false
field_execution_performed = false
markers_created = false
report_created = false
result_decision_permitted = false
claims_permitted = false
```

## Evidenzgrenze

S1-EC22 bestaetigt Pfadneuheit, Ressourcen, Planlast, Supportinventar und
No-Retry-Politik zum Messzeitpunkt. Es bestaetigt weder Laufzeiterfolg noch
eine spaetere Feldantwort. Auch ein erfolgreicher S1-EC23-Lauf darf nur
Rohmetriken und Kontrollen publizieren; die Forschungsentscheidung bleibt
ein getrennter Folgeschritt.

## Bester naechster Schritt

S1-EC23 sollte den persistenten S1-EC19-Bericht unter seinem Schutzhash
laden, die sechs aktiven `r2/r4/r8`-Zustaende als eingefrorene Quellen
verwenden und genau eine `200/400/800`-Probe mit allen sieben Armen
ausfuehren. Vor dem Attempt sind Ressourcen erneut zu messen. Bericht,
Reread und typisierte Rohmetriken muessen verifiziert sein, bevor der Attempt
entfernt wird. Keine Ergebnisentscheidung und kein Claim gehoeren in diesen
Lauf.
