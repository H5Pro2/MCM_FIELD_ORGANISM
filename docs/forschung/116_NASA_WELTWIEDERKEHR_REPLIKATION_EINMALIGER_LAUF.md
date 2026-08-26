# NASA-Weltwiederkehr: einmaliger sechsarmiger Replikationslauf

## Entscheidung

Die endgueltige Startfreigabe war positiv. Genau ein Aufruf von `tools/run_public_av_return_replication.py` wurde ausgefuehrt.

Der CLI beendete mit `exit 0`. Es wurde keine Wiederholung gestartet.

## Laufgrenze

```text
execution_id:              public.av.nasa-earthrise.return-replication.execution.v1
runner_id:                 public.av.nasa-earthrise.return-replication.runner.wiring.v1
preflight_id:              public.av.nasa-earthrise.return-replication.preflight.v1
source_id:                 public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
clock_id:                  public.media.pts_ns
stage_duration_ticks:      500000000
resolution_duration_ticks: 100000000
authorized_repeat_count:   1
execution_started:         true
execution_completed:       true
```

## Arm-Ergebnisse

```text
return.continued.full_state
  stage_one_events: 56
  stage_two_events: 56
  contact_mode: audited_reduced_sequence
  post_resolution_snapshot: aa72b3f06051dfb8b9cd253369ba838ae0b039ca3eb7ae7ba105a7819c7a97b9
  stage_two_layer: c9a5d0fb4bf88f975a5d35eda11a473f159e8812c0aa7f3646666ed2c73b68ce
  stage_two_snapshot: f1600c73655b04ffe68d83c4b7b43939ffcf7215ea82cebd4262200147e78988

return.fresh_stage_two
  stage_one_events: 56
  stage_two_events: 56
  contact_mode: audited_reduced_sequence
  post_resolution_snapshot: null
  stage_two_layer: 98e017ef50d98c2178ef6b5d43376d46ee2e2e3c6a7353c774e82ff605adc477
  stage_two_snapshot: 2144b71530756e149b0e2efa026a9cd0e3cbd4b636c2d89eb26abb4505992535

control.activation_only_carry
  stage_one_events: 56
  stage_two_events: 56
  contact_mode: audited_reduced_sequence
  intervention: observer.shared-field-component.reset_afterimage_preserve_activation.v1
  stage_two_layer: 23337bf73094ef5ebcc8c025ceb24df6a80c8b7988b1d8bcdc93f80ad80bd5ae
  stage_two_snapshot: 6994c117a57d3687004f21ca055c418cc0e99ad13b31565cfa02bb5b4841dae3

control.afterimage_only_carry
  stage_one_events: 56
  stage_two_events: 56
  contact_mode: audited_reduced_sequence
  intervention: observer.shared-field-component.reset_activation_preserve_afterimage.v1
  stage_two_layer: 8895dff3ed67d43d3e991ed6809403590ed3246008fcb552d60b857fab071442
  stage_two_snapshot: 1150547768330ccec4c7f62bea40ab84732db2a88305c2511a410a1693a478ba

control.stage_two_order_permuted
  stage_one_events: 56
  stage_two_events: 56
  contact_mode: permuted_reduced_sequence
  stage_two_layer: ef925adc930cf59d6f7e460fbe35b9067b2239dee79e30696d258ad415098f26
  stage_two_snapshot: ddaceb1ec2bcee20148553f94467bbd1d3d51c55fc5f712186e52a34339f09e4

control.stage_two_sequence_withheld
  stage_one_events: 56
  stage_two_events: 0
  contact_mode: withheld_contact_free
  stage_two_layer: 36b76be4958ce1e40732289a1e09dcfce7df2b3160a8e5425ddb294fa5d8bc66
  stage_two_snapshot: 44faae49909627709335c493e087d582271119393b9e81610c92c2d470bbbf48
```

Alle Arme besitzen denselben Stufe-eins-Snapshot:

```text
e987feafce00699b1945e666d9d954716df53a935ecd9a005bf9573cb13c4c51
```

## Paarweise technische Differenzen

Arm-Reihenfolge:

```text
0 return.continued.full_state
1 return.fresh_stage_two
2 control.activation_only_carry
3 control.afterimage_only_carry
4 control.stage_two_order_permuted
5 control.stage_two_sequence_withheld
```

Aktivierung L-inf:

```text
0: 0.0, 0.017293651956615398, 0.0, 0.017293651956615398, 0.012491996276939484, 0.021061313972438742
1: 0.017293651956615398, 0.0, 0.017293651956615398, 0.0, 0.010251972869725621, 0.011481558846333728
2: 0.0, 0.017293651956615398, 0.0, 0.017293651956615398, 0.012491996276939484, 0.021061313972438742
3: 0.017293651956615398, 0.0, 0.017293651956615398, 0.0, 0.010251972869725621, 0.011481558846333728
4: 0.012491996276939484, 0.010251972869725621, 0.012491996276939484, 0.010251972869725621, 0.0, 0.011078336010613223
5: 0.021061313972438742, 0.011481558846333728, 0.021061313972438742, 0.011481558846333728, 0.011078336010613223, 0.0
```

Nachhall L-inf:

```text
0: 0.0, 0.017580295681599252, 0.003527301811182163, 0.014223839182877845, 0.009650827900181767, 0.0017208269679413624
1: 0.017580295681599252, 0.0, 0.014223839182877824, 0.0035273018111821545, 0.02718958763859674, 0.01733642864552728
2: 0.003527301811182163, 0.014223839182877824, 0.0, 0.010867382684156419, 0.013139919076486147, 0.003112589462649456
3: 0.014223839182877845, 0.0035273018111821545, 0.010867382684156419, 0.0, 0.023833131139875334, 0.013979972146805875
4: 0.009650827900181767, 0.02718958763859674, 0.013139919076486147, 0.023833131139875334, 0.0, 0.010326414905583232
5: 0.0017208269679413624, 0.01733642864552728, 0.003112589462649456, 0.013979972146805875, 0.010326414905583232, 0.0
```

Layer- und Snapshot-Digests waren nur diagonal gleich; alle nichtidentischen Armvergleiche hatten unterschiedliche Layer- und Snapshot-Digests.

## Technischer Befund

Der einmalige sechsarmige Lauf trennt den frischen Stufe-zwei-Pfad, die volle Feldfortsetzung, die beiden Komponenteninterventionen, die permutierte Stufe-zwei-Sequenz und die kontaktfreie Stufe-zwei-Fortschreibung technisch voneinander. Die Aktivierungs- und Nachhallmatrizen enthalten die vorregistrierten paarweisen Differenzmessungen.

Dies ist kein Nachweis von Memory, Bedeutung, Organisation oder eigenstaendiger KI.

## Claim-Grenze

```text
memory_threshold_defined:       false
organization_threshold_defined: false
memory_claim_allowed:           false
meaning_claim_allowed:          false
organization_claim_allowed:     false
ai_claim_allowed:               false
```
