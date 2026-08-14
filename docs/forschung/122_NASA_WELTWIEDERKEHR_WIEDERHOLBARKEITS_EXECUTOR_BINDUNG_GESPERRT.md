# NASA-Weltwiederkehr: Wiederholbarkeits-Executor-Bindung gesperrt

## Zweck

Dieser Vertrag bindet die drei vorregistrierten Wiederholungsslots an je eine künftige
Executor-Identität. Er erzeugt keinen Callable-Executor, keine Einstiegspunktinstanz
und startet keinen Lauf.

## Struktur

```text
repeat_index_set:                         1, 2, 3
all_slots_have_executor_identity:         true
executor_binding_ids_unique:              true
future_executor_ids_unique:               true
preflight_runner_permutation_bound_per_slot:true
```

Pro Slot sind gebunden:

```text
positive_slot_start_bound:       true
preflight_identity_bound:        true
runner_identity_bound:           true
permutation_identity_bound:      true
executor_identity_bound:         true

executor_callable_created:       false
entrypoint_instance_created:     false
executor_bound_to_entrypoint:    false
start_allowed:                   false
repeat_run_started:              false
prior_executor_binding_reusable: false
```

Die Bindung bleibt indexgebunden. Basisvorabnahme, Basisrunner und Permutationsvertrag
werden pro Slot als Identitäten und Digestbezug festgehalten.

## Sperren

```text
executor_binding_allowed:        false
start_allowed:                   false
repeatability_run_allowed:       false
automatic_repeat_loop_available: false
stability_threshold_defined:     false
memory_claim_allowed:            false
meaning_claim_allowed:           false
organization_claim_allowed:      false
ai_claim_allowed:                false
```

Der Vertrag ist damit nur eine technische Vorbindung fuer eine moegliche spaetere,
separat freizugebende Ausfuehrungsinstanz. Er ist keine Organismusfunktion und kein
Befund zu Memory, Bedeutung, Organisation oder KI-Faehigkeit.

## Quellen

- aktueller Uebergabeauftrag
- `mcm_field_organism/public_av_return_replication_repeatability_slot_start.py`
- `mcm_field_organism/public_av_return_replication_repeatability_preflight.py`
- `mcm_field_organism/public_av_return_replication_runner.py`
- `mcm_field_organism/public_av_return_permutation_contract.py`
- `mcm_field_organism/public_av_return_replication_execution.py`
