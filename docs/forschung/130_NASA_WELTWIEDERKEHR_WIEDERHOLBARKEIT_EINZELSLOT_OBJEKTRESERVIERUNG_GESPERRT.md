# NASA-Weltwiederkehr: Einzelslot-Objektreservierung gesperrt

Der Vertrag reserviert fuer genau einen ausgewaehlten Wiederholungsindex
zukuenftige Objektidentitaeten fuer Callable und One-Shot-Gate. Die logischen
Callable-, Gate-, Executor-, Kandidaten- und Quellenidentitaeten bleiben
unveraendert gebunden. Die beiden anderen Slots bleiben unselektiert.

```text
exactly_one_order_bound:              true
callable_object_identity_reserved:    true
gate_object_identity_reserved:        true
logical_identities_unchanged:         true
selected_slot_still_fresh:            true

callable_object_created:              false
gate_object_created:                  false
object_factory_created:               false
binding_performed:                    false
scheduler_available:                  false
media_decode_allowed:                 false
receptor_feed_allowed:                false
start_release_granted:                false
repeatability_run_allowed:            false
memory_claim_allowed:                 false
meaning_claim_allowed:                false
organization_claim_allowed:           false
ai_claim_allowed:                     false
```

Eine Reservierung ist keine Instanziierung. Ein Erzeugungsversuch wird
abgewiesen; die Audit-CLI prueft nur Quelle und Vertragskette.
