# NASA-Weltwiederkehr: gesperrter Slot-Startvertrag

## Gegenstand

Die drei positiven Slot-Vorabnahmen sind jeweils einem eindeutigen Wiederholungsindex und einer eindeutigen künftigen One-Shot-Einstiegspunkt-Identität zugeordnet. Es wurde kein Einstiegspunkt instanziiert, kein Executor gebunden und keine Wiederholung gestartet.

## Bindungen

```text
repeat_index: 1, 2, 3
binding_ids_unique: true
entrypoint_ids_unique: true
all_positive_preflights_bound_once: true
fresh_entrypoint_per_slot_required: true
```

Obwohl die drei Basisvorabnahmen wegen identischer Verträge dieselbe technische Basis-ID tragen, verhindern die indexgebundenen Bindungs- und Einstiegspunkt-IDs eine Verwechslung der Wiederholungsslots.

## Sperren

```text
entrypoint_instance_created:     false
executor_bound:                  false
start_allowed:                   false
executor_binding_allowed:        false
repeatability_run_allowed:       false
automatic_repeat_loop_available: false
stability_threshold_defined:     false
```

Ein verbrauchter Slot oder eine bereits gestartete Wiederholung ist nicht bindbar. Frühere Bindungen und Ausführungsbelege sind nicht wiederverwendbar.

## Aussagegrenze

Der Vertrag ist nur eine technische Zuordnungsschicht. Er enthält keine Stabilitätsmessung und erlaubt keine Memory-, Bedeutungs-, Organisations- oder KI-Claims.
