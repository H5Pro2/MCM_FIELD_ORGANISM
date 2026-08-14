# NASA-Weltwiederkehr: Einzelslot-Instanziierungsauftrag gesperrt

## Zweck

Dieser Vertrag leitet aus der positiven finalen Ausfuehrungsvorabnahme einen auf
genau einen Wiederholungsindex begrenzten technischen Instanziierungsauftrag ab.
Er waehlt einen frischen Slot aus und bindet dessen Identitaeten, erzeugt aber
keine Objekte und startet keinen Lauf.

## Gepruefte Auswahl

```text
selected_repeat_index:          1 oder 2 oder 3
exactly_one_slot_selected:      true
selected_slot_is_fresh:         true
selected_slot_identity_bound:   true
candidate_identity_bound:       true
callable_identity_bound:        true
executor_identity_bound:        true
gate_identity_bound:            true
source_identity_bound:          true
```

Die nicht gewaehlt bleibenden Slots werden nur als Indexmenge dokumentiert. Es
wird keine automatische Ueberleitung auf diese Slots angelegt.

## Sperren

```text
callable_object_created:     false
gate_instance_created:       false
binding_performed:           false
scheduler_available:         false
media_decode_allowed:        false
receptor_feed_allowed:       false
start_release_granted:       false
repeatability_run_allowed:   false
repeat_run_started:          false
stability_threshold_defined: false
memory_claim_allowed:        false
meaning_claim_allowed:       false
organization_claim_allowed:  false
ai_claim_allowed:            false
```

Ein Instanziierungsversuch ueber diesen Vertrag wird technisch abgewiesen. Die
Audit-CLI prueft nur Dateiintegritaet und Vertragskonsistenz. Sie decodiert kein
Medium, speist keine Rezeptoren und startet keinen Feld- oder Wiederholungslauf.

## Aussagegrenze

Der Vertrag belegt ausschliesslich die konsistente technische Auswahl eines
spaeter moeglichen Einzelslots. Er ist keine Startfreigabe und kein Befund zu
Stabilitaet, Memory, Bedeutung, Organisation oder KI.
