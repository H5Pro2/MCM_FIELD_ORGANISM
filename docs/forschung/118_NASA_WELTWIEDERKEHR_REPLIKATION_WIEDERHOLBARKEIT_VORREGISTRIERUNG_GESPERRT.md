# NASA-Weltwiederkehr: Wiederholbarkeit der technischen Kausalkontraste

## Entscheidung

Die laufgesperrte Vorregistrierung zur unabhaengigen Wiederholbarkeit der vier technischen Kausalkontraste ist erstellt.

Es wurde kein Runner implementiert und kein weiterer Replikationslauf ausgefuehrt.

## Wiederholungsrahmen

```text
preregistration_id:        public.av.nasa-earthrise.return-replication.repeatability-preregistration.v1
base_preregistration_id:   public.av.nasa-earthrise.return-replication.v1
independent_repeat_count:  3
repeat_index_set:          1, 2, 3
source_id:                 public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
clock_id:                  public.media.pts_ns
```

Jede Wiederholung muss als unabhaengiger Lauf mit frischem Feld am Repeat-Start behandelt werden. Es darf keinen Zustandsuebertrag zwischen Wiederholungen und keine adaptive Parameterveraenderung zwischen Wiederholungen geben.

## Identische Vertragsparameter

Vor jeder spaeteren Ausfuehrungsfreigabe muessen identisch bleiben:

- Quellenvertrag und lokale Dateiintegritaet,
- Permutationsvertragsdigest,
- Komponenten-Interventionsvertrag,
- sechsarmige Runnerverdrahtung,
- Ausfuehrungsvorabnahme-Gate,
- Stufe-eins-Dauer, Aufloesungsdauer und Stufe-zwei-Dauer,
- Feldparameter,
- oeffentliche Medienuhr.

## Vorregistrierte Kontraste

```text
full_state_vs_fresh_stage_two:
  return.continued.full_state
  return.fresh_stage_two

activation_only_vs_afterimage_only:
  control.activation_only_carry
  control.afterimage_only_carry

full_state_vs_permuted_stage_two:
  return.continued.full_state
  control.stage_two_order_permuted

full_state_vs_withheld_stage_two:
  return.continued.full_state
  control.stage_two_sequence_withheld
```

## Rein technische Stabilitaetsmessungen

Vorregistriert sind ausschliesslich:

- `per_repeat_activation_linf`,
- `per_repeat_afterimage_linf`,
- `per_repeat_layer_digest_equality`,
- `per_repeat_snapshot_digest_equality`,
- `cross_repeat_activation_linf_min_max_range`,
- `cross_repeat_afterimage_linf_min_max_range`,
- `cross_repeat_digest_equality_pattern_consistency`,
- `withheld_stage_two_event_count_consistency`.

Aggregiert werden duerfen nur technische Minima, Maxima, Spannweiten, Digest-Musterzaehlungen und Repeat-Indizes.

## Sperren

```text
runner_implementation_allowed:     false
repeatability_run_allowed:         false
memory_threshold_defined:          false
organization_threshold_defined:    false
positive_effect_required:          false
causal_mechanism_claim_allowed:    false
memory_claim_allowed:              false
meaning_claim_allowed:             false
organization_claim_allowed:        false
ai_claim_allowed:                  false
```

Diese Vorregistrierung erlaubt keine Memory-, Bedeutungs-, Organisations- oder KI-Claims.
