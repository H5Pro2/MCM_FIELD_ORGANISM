# NASA-Weltwiederkehr: Finale Wiederholungs-Orchestrierung gesperrt

## Zweck

Der Vertrag weist die drei vollstaendig vorbereiteten Identitaetspfade als
geordnete technische Startkandidaten 1, 2 und 3 aus. Ein Startkandidat ist nur
eine konsistente Identitaetskette und keine Startfreigabe.

## Garantien

- feste Reihenfolge 1, 2, 3
- eindeutige Kandidaten-, Callable-, Gate- und Executor-Identitaeten
- keine Zustandsuebernahme zwischen Kandidaten
- frische Objekte bleiben fuer eine spaetere, separate Freigabe erforderlich

## Sperren

```text
callable_objects_created:        false
gate_instances_created:          false
bindings_performed:              false
scheduler_created:               false
automatic_transition_available: false
start_release_granted:           false
repeatability_run_allowed:       false
stability_threshold_defined:     false
memory_claim_allowed:            false
meaning_claim_allowed:           false
organization_claim_allowed:      false
ai_claim_allowed:                false
```

Der Vertrag enthaelt keinen Scheduler, Iterator, Callback oder Startbefehl. Ein
Startversuch wird abgewiesen. Die Audit-CLI prueft nur Dateiintegritaet und
Vertragskonsistenz; sie decodiert kein Medium und startet keinen Feldlauf.
