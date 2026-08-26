# NASA-Weltwiederkehr: Wiederholbarkeits-Ausfuehrungsvorabnahme gesperrt

## Entscheidung

Die Ausfuehrungsvorabnahme fuer drei unabhaengige Wiederholungsslots ist implementiert. Sie prueft pro Slot eine separate positive und unverbrauchte One-Shot-Freigabe, identische Vertragsparameter und fehlende Zustandsuebernahme.

Es wurde keine Wiederholung ausgefuehrt, kein Medium decodiert und kein Rezeptor gespeist.

## Slot-Grenze

```text
repeat_index_set: 1, 2, 3
repeat_count_authorized_per_slot: 1
positive_one_shot_release_available: true
one_shot_release_unconsumed: true
fresh_runner_instance_required: true
fresh_field_at_repeat_start: true
cross_repeat_state_carry_absent: true
prior_execution_receipt_reusable: false
slot_executable: false
```

Jeder Slot ist nur als technisches Gate beschrieben. Ein verbrauchter One-Shot-Beleg oder ein abweichender Medienpfad wird konstruktiv abgewiesen.

## Vertragsidentitaet

Die Vorabnahme verlangt:

- identischen Quellenvertrag,
- identische lokale Dateiintegritaet,
- identische Vorregistrierungs-, Kompatibilitaets- und Permutationsvertragsidentitaeten,
- identischen Permutationsdigest,
- identische Feldparameterrollen,
- identische sechsarmige Runnerverdrahtung,
- keine Zustandsuebernahme zwischen Repeat-Indizes.

## Gesamtsperren

```text
repeatability_preflight_complete: true
repeatability_run_allowed:        false
automatic_repeat_loop_available:  false
media_decode_allowed:             false
receptor_feed_allowed:            false
stability_threshold_defined:      false
memory_threshold_defined:         false
organization_threshold_defined:   false
causal_mechanism_claim_allowed:   false
memory_claim_allowed:             false
meaning_claim_allowed:            false
organization_claim_allowed:       false
ai_claim_allowed:                 false
```

Diese Vorabnahme erlaubt keine Wiederholungskette und definiert keine Stabilitaets-, Memory- oder Organisationsschwelle.
