# Einzelslot Callable-Factory-Aufrufsausfuehrungsvorabnahme (gesperrt)

## Zweck

Dieser Vertrag bindet fuer genau einen Wiederholungsindex die positive,
weiterhin laufgesperrte Callable-Factory-Aufrufsauftragsabnahme und genau einen
unverbrauchten Callable-Factory-Aufruf als zukuenftigen Ausfuehrungskandidaten.

## Vorabnahmegrenze

- Der Callable-Factory-Aufruf bleibt einmalig, unverbraucht und nicht ausgefuehrt.
- Der Gate-Factory-Schritt bleibt unselektiert, unberuehrt und nicht ausgefuehrt.
- Factory- und Callable-Referenzen werden nicht gespeichert.
- Ein tatsaechlicher Factory-Aufruf, Instanzerzeugung und Bindung bleiben gesperrt.
- Medien-Decode, Rezeptorzufuhr, Scheduler und Laufstart bleiben gesperrt.
- Memory-, Bedeutungs-, Organisations- und KI-Claims bleiben gesperrt.

## Befundschema

```text
selected_repeat_index:                              1, 2 oder 3
positive_call_order_acceptance_bound:               true
exactly_one_call_execution_candidate_bound:         true
callable_factory_call_candidate_unconsumed:         true
callable_factory_identity_bound:                    true
callable_constructor_identity_bound:                true
future_callable_object_identity_bound:              true
gate_factory_step_unselected:                       true
gate_factory_step_untouched:                        true
gate_factory_step_still_unexecuted:                 true
selected_slot_still_fresh:                          true
callable_factory_call_execution_preflight_complete: true

callable_factory_reference_stored:                  false
gate_factory_reference_stored:                      false
callable_reference_stored:                          false
factory_function_called:                            false
callable_factory_called:                            false
gate_factory_called:                                false
callable_object_created:                            false
gate_object_created:                                false
constructor_invoked:                                false
binding_performed:                                  false
scheduler_available:                                false
media_decode_allowed:                               false
receptor_feed_allowed:                              false
start_release_granted:                              false
repeatability_run_allowed:                          false
repeat_run_started:                                 false
stability_threshold_defined:                        false
memory_claim_allowed:                               false
meaning_claim_allowed:                              false
organization_claim_allowed:                         false
ai_claim_allowed:                                   false
```

## Abweisung

Ein Gate-Schritt als Ausfuehrungskandidat, veraenderte Identitaeten,
verbrauchte Schritte und aktivierte Ausfuehrungsfelder werden technisch
abgewiesen. Der JSON-Vertrag enthaelt keine ausfuehrbaren Referenzen,
Instanzen, Ergebnisse oder Claim-Scores.

## Aussagegrenze

Die Vorabnahme belegt ausschliesslich die Konsistenz eines gesperrten
zukuenftigen Callable-Factory-Aufrufs als Ausfuehrungskandidat. Sie belegt
keinen Factory-Aufruf, Weltkontakt, Memory, Bedeutung, innere Organisation oder
eigenstaendige KI.
