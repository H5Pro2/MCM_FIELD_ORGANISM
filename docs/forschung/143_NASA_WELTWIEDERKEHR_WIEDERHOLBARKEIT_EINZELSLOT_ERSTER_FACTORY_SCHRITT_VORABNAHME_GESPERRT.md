# NASA-Weltwiederkehr Wiederholbarkeit: gesperrte Einzelslot-Vorabnahme des ersten Factory-Schritts

## Zweck

Dieses Dokument beschreibt den gesperrten Vorabnahmevertrag fuer den ersten Factory-Ausfuehrungsschritt eines ausgewaehlten Wiederholungs-Slots. Der Vertrag waehlt ausschliesslich den unverbrauchten Callable-Factory-Schritt aus der positiven Ausfuehrungsauftragsabnahme aus.

## Freigegebene Bindungen

- genau ein `selected_repeat_index` aus `1`, `2` oder `3`
- positive Einzelslot-Factory-Ausfuehrungsauftragsabnahme
- erster Future-Step mit Rolle `callable_factory`
- Callable-Factory-Identitaet
- Callable-Konstruktoridentitaet
- zukuenftige Callable-Objektidentitaet
- unberuehrter zweiter Gate-Factory-Step als weiterhin unverbrauchte Restbindung

## Gesperrte Flaechen

- keine Factory-Referenz
- keine Callable-Referenz
- kein Factory-Aufruf
- keine Instanzerzeugung
- kein Konstruktoraufruf
- keine Bindung
- kein Scheduler
- kein Medien-Decode
- keine Rezeptorzufuhr
- kein Laufstart
- keine Stabilitaetsschwelle
- kein Memory-, Bedeutungs-, Organisations- oder KI-Claim

## Befundschema

```text
positive_execution_order_acceptance_bound:       true
exactly_one_callable_factory_step_selected:      true
callable_factory_step_unconsumed:                true
callable_factory_identity_bound:                 true
callable_constructor_identity_bound:             true
future_callable_object_identity_bound:           true
gate_factory_step_unselected:                    true
gate_factory_step_untouched:                     true
gate_factory_step_still_unexecuted:              true
selected_slot_still_fresh:                       true
first_factory_step_preflight_complete:           true

callable_factory_reference_stored:               false
gate_factory_reference_stored:                   false
callable_reference_stored:                       false
factory_function_called:                         false
callable_factory_called:                         false
gate_factory_called:                             false
callable_object_created:                         false
gate_object_created:                             false
constructor_invoked:                             false
binding_performed:                               false
scheduler_available:                             false
media_decode_allowed:                            false
receptor_feed_allowed:                           false
start_release_granted:                           false
repeatability_run_allowed:                       false
repeat_run_started:                              false
stability_threshold_defined:                     false
memory_claim_allowed:                            false
meaning_claim_allowed:                           false
organization_claim_allowed:                      false
ai_claim_allowed:                                false
```

## Abweisung

Ein Ausfuehrungsversuch ueber die Vorabnahme wird technisch abgewiesen. Vertauschte Schritte, verbrauchte Schritte, ein beruehrter Gate-Factory-Schritt oder aktivierte Ausfuehrungsfelder machen den Vertrag ungueltig.
