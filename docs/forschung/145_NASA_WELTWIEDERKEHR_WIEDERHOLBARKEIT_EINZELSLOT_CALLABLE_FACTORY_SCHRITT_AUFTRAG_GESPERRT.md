# NASA-Weltwiederkehr Wiederholbarkeit: gesperrter Einzelslot-Callable-Factory-Schritt-Auftrag

## Zweck

Dieses Dokument beschreibt den gesperrten Auftragsvertrag fuer den ersten Callable-Factory-Ausfuehrungsschritt eines ausgewaehlten Wiederholungs-Slots. Der Vertrag leitet aus der positiven ersten Schritt-Abnahme genau einen zukuenftigen, einmaligen Callable-Factory-Auftrag ab.

## Freigegebene Bindungen

- genau ein `selected_repeat_index` aus `1`, `2` oder `3`
- positive Abnahme des ersten Factory-Schritts
- ein zukuenftiger Callable-Factory-Auftrag
- Callable-Factory-Identitaet
- Callable-Konstruktoridentitaet
- zukuenftige Callable-Objektidentitaet
- Gate-Factory-Step als unselektierte, unberuehrte und nicht ausgefuehrte Restbindung

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
positive_first_step_acceptance_bound:         true
exactly_one_callable_factory_order_derived:   true
callable_factory_order_one_time:              true
callable_factory_order_unexecuted:            true
callable_factory_identity_bound:              true
callable_constructor_identity_bound:          true
future_callable_object_identity_bound:        true
gate_factory_step_unselected:                 true
gate_factory_step_untouched:                  true
gate_factory_step_still_unexecuted:           true
selected_slot_still_fresh:                    true
callable_factory_step_order_complete:         true

callable_factory_reference_stored:            false
gate_factory_reference_stored:                false
callable_reference_stored:                    false
factory_function_called:                      false
callable_factory_called:                      false
gate_factory_called:                          false
callable_object_created:                      false
gate_object_created:                          false
constructor_invoked:                          false
binding_performed:                            false
scheduler_available:                          false
media_decode_allowed:                         false
receptor_feed_allowed:                        false
start_release_granted:                        false
repeatability_run_allowed:                    false
repeat_run_started:                           false
stability_threshold_defined:                  false
memory_claim_allowed:                         false
meaning_claim_allowed:                        false
organization_claim_allowed:                   false
ai_claim_allowed:                             false
```

## Abweisung

Ein Ausfuehrungsversuch ueber den Auftrag wird technisch abgewiesen. Vertauschte Schritte, ein beruehrter Gate-Factory-Schritt, verbrauchte Schritte oder aktivierte Ausfuehrungsfelder machen den Vertrag ungueltig.
