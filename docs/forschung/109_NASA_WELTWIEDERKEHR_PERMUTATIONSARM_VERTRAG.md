# NASA Weltwiederkehr - Permutationsarm-Vertrag

## Pruefentscheidung

Der Permutationsarm der Replikationsvorregistrierung ist jetzt vollstaendig observerseitig spezifiziert. Es wurde kein Replikationsrunner implementiert und kein Replikationslauf ausgefuehrt.

## Arm

```text
arm_id:               control.stage_two_order_permuted
source_sequence_id:   public.av.nasa-earthrise.0p5s.reduced.v1
permuted_sequence_id: public.av.nasa-earthrise.0p5s.reduced.permuted-order.v1
```

## Deterministische Permutationsabbildung

Die Permutation ist eine Rangumkehr je Modalitaet:

```text
auditory: 41 Frames, source rank i -> time-slot rank 40 - i
visual:   15 Frames, source rank i -> time-slot rank 14 - i
```

Die Zeit-Slots selbst bleiben die original sortierten Stufe-zwei-Zeitfenster der jeweiligen Modalitaet. Es gibt kein Jittering, kein Resampling und keine neuen Ueberlappungen.

## Ereigniszeitvertrag

```text
clock_id:                 public.media.pts_ns
stage_two_interval_ticks: [600000000, 1100000000]
stage_two_tick_offset:    600000000
time_slot_rule:           preserve_original_sorted_time_slots_per_modality
overlap_policy:           no_new_overlap_no_time_jitter_no_resampling
```

## Sequenz-Digests

Die permutierten Sequenz-Digests sind kanonische SHA-256-Digests aus Quelldigest, Mapping und Ereigniszeitvertrag:

```text
auditory_permuted_sequence_digest: ebec7efcc7015ea990acc35f2e7a47a68824c7b6794a6cf71d901219f7e6e82c
visual_permuted_sequence_digest:   d28261faedc50bc2f87215f48d4e81454e9e62f28920f27fa7e77fe9894907f7
contract_digest:                   0f8de92de09bc9d9c7ea7ec9c02882aefc01e8c393ae1049a56f5c121cf60437
```

Diese Digests sind Vertragsdigests, keine neu decodierten Medienbefunde.

## Sperren

```text
fully_specified:                    true
runner_implementation_allowed:      false
replication_run_allowed:            false
artificial_media_events_introduced: false
field_parameters_changed:           false
memory_claim_allowed:               false
meaning_claim_allowed:              false
organization_claim_allowed:         false
ai_claim_allowed:                   false
```

## Grenze

Der Vertrag fuehrt keine Rezeptorsequenztransformation aus und speist kein Feld. Er entfernt nur den vorherigen Spezifikationsblocker des Permutationsarms.

Der weiterhin offene Blocker sind die Komponenten-Interventionsarme. Dafuer ist separat zu pruefen, ob ein allgemeiner inhaltsneutraler Interventionsvertrag technisch und methodisch begruendbar ist.
