# NASA-Weltwiederkehr: Einzelslot-Objektkonstruktion gesperrt

## Zweck

Dieser Vertrag uebernimmt eine Einzelslot-Objektreservierung und legt nur die
zulaessigen kuenftigen Konstruktoridentitaeten fuer Callable- und One-Shot-Gate-
Objekt fest. Er ruft keine Fabrik auf, erzeugt keine Instanz, fuehrt keine
Bindung durch und startet keinen Lauf.

## Gebundene Struktur

```text
selected_repeat_index:                1, 2 oder 3
exactly_one_reservation_bound:        true
reserved_object_identities_bound:     true
constructor_identities_declared:      true
callable_constructor_allowed_later:   true
gate_constructor_allowed_later:       true
selected_slot_still_fresh:            true
```

Die logischen Callable-, Gate-, Executor-, Kandidaten- und Quellenidentitaeten
bleiben unveraendert rueckverfolgbar. Die beiden nicht gewaehlt bleibenden Slots
werden nur als Indexmenge dokumentiert.

## Sperren

```text
callable_factory_called:       false
gate_factory_called:           false
callable_object_created:       false
gate_object_created:           false
constructor_invoked:           false
binding_performed:             false
scheduler_available:           false
media_decode_allowed:          false
receptor_feed_allowed:         false
start_release_granted:         false
repeatability_run_allowed:     false
repeat_run_started:            false
stability_threshold_defined:   false
memory_claim_allowed:          false
meaning_claim_allowed:         false
organization_claim_allowed:    false
ai_claim_allowed:              false
```

Ein Konstruktionsversuch ueber diesen Vertrag wird technisch abgewiesen. Die
Audit-CLI prueft nur Dateiintegritaet und Vertragskonsistenz. Sie decodiert kein
Medium, speist keine Rezeptoren und startet keinen Feld- oder Wiederholungslauf.

## Aussagegrenze

Der Vertrag ist keine Startfreigabe und kein Befund zu Stabilitaet, Memory,
Bedeutung, Organisation oder KI.
