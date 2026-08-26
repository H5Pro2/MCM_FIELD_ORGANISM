# W2-A: Bestandsaudit der oeffentlichen Paketoberflaeche

Stand: 2026-08-09

Entscheidung: `ROOT_API_MIXED_CURRENT_SURFACE_REQUIRES_COMPATIBLE_SPLIT`

Auditart: statisch

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Auftrag

W2-A prueft die Reexporte aus `mcm_field_organism/__init__.py` gegen den
S1-AA-Entwicklungsanschluss. Jeder Reexport erhaelt genau eine operative
Kategorie. Es werden keine Importe veraendert und keine Module geloescht.

## Inventar

Die Root-Oberflaeche reexportiert derzeit:

```text
Importmodule: 155
Symbole:       1267
```

Die Menge ist keine kuratierte aktuelle Architektur-API. Sie vereinigt
Produktionsbausteine, Referenzmechaniken, historische Forschungszweige,
inaktive Live-/Physikpfade und interne Auditwerkzeuge in einem Namensraum.

## Kategorien und Umfang

Die primaere Modulklassifikation ergibt:

| Kategorie | Module | Symbole vor gemischten Ausnahmen |
|---|---:|---:|
| `CURRENT_CONTROLLED_FIELD_API` | 30 | 183 |
| `REFERENCE_ONLY` | 12 | 87 |
| `HISTORICAL_OR_PAUSED` | 55 | 547 |
| `LIVE_OR_PHYSICAL_INACTIVE` | 10 | 80 |
| `PRIVATE_TOOLING` | 48 | 370 |
| **Gesamt** | **155** | **1267** |

Nach den unten gebundenen drei Symbolausnahmen lautet die exakte
Exportzuordnung:

```text
CURRENT_CONTROLLED_FIELD_API: 182
REFERENCE_ONLY:                89
HISTORICAL_OR_PAUSED:         547
LIVE_OR_PHYSICAL_INACTIVE:     79
PRIVATE_TOOLING:              370
Gesamt:                      1267
```

Damit gehoeren nur 182 von 1267 Root-Symbolen zur gegenwaertigen
kontrollierten Feldoberflaeche. Auch diese 182 sind noch ein Bestandskorridor,
keine bereits minimal kuratierte Soll-API.

## CURRENT_CONTROLLED_FIELD_API

Primaer aktuelle Module:

```text
asynchronous_receptor_events
audio_video_neutral_field_runtime
broadband_hearing_path
browser_payload_runtime
browser_payload_source
browser_receptor_bridge
browser_world_contract
controlled_audio_phase_source
external_media_observation_contract
field_step_time
field_time_partition
finite_multimodal_field_run
finite_video_path
log_spectral_receptor
mcm_neuron
mcm_neuron_layer
neutral_asynchronous_field_runtime
neutral_field_session
neutral_local_field_substrate
public_visual_world
receptor_contract
receptor_distributor
receptor_process_contract
receptor_surface
receptor_temporal_support
sensor_interface
shared_field_session
shared_mcm_field
transient_dock_trajectory
transient_neuron_input
```

Diese Gruppe deckt kontrollierte Quellen, Rezeptoren, Zeituebergabe, Docks,
gemeinsames Feld, neutrale Sitzungen, Browserpayloads und Snapshot/Restore ab.
Browserpayload bezeichnet dabei ausschliesslich die kontrollierte digitale
Testwelt und keine Kamera.

## REFERENCE_ONLY

```text
auditory_baselines
carrier_baselines
continuous_world_baselines
local_deformation_baselines
mcm_f3_baseline_coupling
mcm_f3_coupling
mcm_f3_runtime
mcm_local_development_state
mcm_substrate_state
passive_field_controls
s1b_reciprocal_accommodation
s2_reference_baselines
```

Diese Module bleiben fuer F3, lineare Kopplung, Nullpfad und enge
Gegenbaselines verfuegbar. Sie sind keine behauptete produktive
Memoryarchitektur.

## HISTORICAL_OR_PAUSED

```text
abu_interaction_ground_null
condensed_field_form_null_probe
contact_material_admissibility
continuous_two_relation_world
controlled_endogenous_source
current_field_history_null_probe
endogenous_external_overlap_null_probe
endogenous_receptor
field_passivity_null_probe
gf001_local_field_effect_methodology
gf001_local_field_effect_probe
instantaneous_field_flow_null_probe
local_deformation_world
local_synaptic_memory_candidate
local_transition_evidence_probe
mcm_f3_k2b_run
mcm_f3_k2b_source
mcm_f3_public_av_run
mcm_f3_z1_completion_support
mcm_f3_z1_evaluation
mcm_f3_z1_run
mcm_f3_z1_run196
mcm_f3_z1_runner
mcm_f3_z1_source
mcm_f3_z1_trajectory
occluded_continuation_world
occluded_world_intervention_probe
passive_synaptic_memory_comparison
periodic_layer_axis_probe
periodic_sampling_probe
radial_contact_morphology
radial_transport_admissibility
radial_transport_cause_audit
relationship_persistence_contract
s2_reference_runner
s2_reference_worlds
signed_field_flow_transport_counterfactual
simulated_effector_world
simulated_ring_field_path_probe
simulated_world_mcm_path
structural_contact_drive
structural_contact_substrate
synaptic_memory_lifecycle_probe
transition_disposition_falsification_probe
z4a_audio_receptor_source
z4a_browser_receptor_adapter
z4a_component_trajectory
z4a_generic_trajectory_runner
z4a_one_shot
z4a_playwright_audio_smoke
z4a_playwright_capture
z4a_playwright_runtime_binding
z4a_playwright_smoke
z4a_scalar_evaluation
z4a_scalar_measurement_adapter
```

Diese Module bleiben im Repository, gehoeren aber nicht zur aktuellen
Oberflaeche. Insbesondere werden Z4, Lauf 197, geschlossene Memorykandidaten,
endogene Quellen und Kontaktmaterial nicht reaktiviert.

## LIVE_OR_PHYSICAL_INACTIVE

```text
common_receptor_window
independent_visual_target_presenter
live_audio_adapter
live_audio_video_field
live_video_adapter
receptor_time_alignment
visual_mcm_effector_presenter
visual_mcm_effector_sequence
visual_mcm_effector_sequence_presenter
visual_mcm_effector_surface
```

Die Dateien bleiben fuer eine spaetere reale Entwicklungsphase erhalten.
Vorerst sind Kamera, Live-Mikrofon, physische Zielflaechen und
Bildschirm-Welt-Rueckkopplung nicht Teil der aktiven API.

## PRIVATE_TOOLING

```text
adapter_timing_capability
architecture_readiness
asynchronous_dock_adjacency_audit
auditory_field_function_probe
browser_payload_smoke
browser_payload_timing_pair
controlled_audio_video_test_world
controlled_av_source_pair_diagnostic
controlled_temporal_order_probe
field_background_contrast_characterization
field_contact_mass_counterbaseline
field_event_density_resource_characterization
field_input_capacity_audit
field_load_recovery_characterization
field_spatial_load_characterization
finite_audio_video_field_run
finite_linear_temporal_projection_audit
history_sensitive_reentry_probe
local_field_effect_admissibility_contract
local_field_inertia_probe
local_neuron_function_probe
marked_visual_phase_probe
mcm_f3_causal_runner
mcm_f3_controlled_history_source
mcm_f3_e3_baseline_run
mcm_f3_geometry_interventions
mcm_f3_geometry_run
mcm_f3_history_run
neuron_drive_information_audit
passive_field_geometry_control
passive_field_resume_control
passive_field_segmentation_comparison
passive_field_temporal_controls
receptor_delivery_model_probe
receptor_proposal_handoff_audit
receptor_rate_invariance_probe
receptor_state_role_audit
sensory_load_recovery_null_probe
sensory_self_regulation_contract
snapshot_change_baseline_probe
spatial_afterimage_orientation_probe
temporal_compact_summary_collision_audit
temporal_directed_moment_audit
temporal_effect_functional_contract
temporal_functional_equivalence_contract
temporal_input_architecture_audit
temporal_null_representation_map
visual_spatiotemporal_input_probe
```

Diese Module duerfen weiterhin direkt in Tests und Audits importiert werden.
Sie gehoeren nicht in eine kleine aktuelle Root-API.

## Gemischte Symbolausnahmen

Die Modulklassifikation wird fuer genau drei bereits reexportierte Symbole
praezisiert:

| Symbol | Modulklasse | Symbolklasse | Begruendung |
|---|---|---|---|
| `SyntheticAudioFrameSource` | `LIVE_OR_PHYSICAL_INACTIVE` | `CURRENT_CONTROLLED_FIELD_API` | rein synthetische kontrollierte Audioquelle |
| `attach_uniform_mcm_substrate` | `CURRENT_CONTROLLED_FIELD_API` | `REFERENCE_ONLY` | aktiviert den optionalen F3-M-Referenzzustand |
| `attach_zero_mcm_local_development` | `CURRENT_CONTROLLED_FIELD_API` | `REFERENCE_ONLY` | aktiviert die lineare S1-B-Referenzrolle |

Das intern verwendete Protokoll `AudioFrameSource` ist derzeit nicht aus der
Root-API reexportiert. Es liegt dennoch in `live_audio_adapter` und wird von
`broadband_hearing_path` sowie `audio_video_neutral_field_runtime` importiert.
Damit haengt aktive kontrollierte Feldtechnik strukturell von einem als
inaktiv klassifizierten Live-Modul ab.

## Hauptbefunde

1. Die Root-API stellt den aktuellen Projektstand nicht dar; 1085 von 1267
   Symbolen gehoeren nicht zur aktiven kontrollierten Feldoberflaeche.
2. Historische Module muessen nicht geloescht werden. Ihre pauschalen
   Root-Reexporte sind das eigentliche Architekturproblem.
3. Die aktive Audiokette besitzt eine konkrete Abhaengigkeitsvermischung:
   geraeteneutrales Protokoll und synthetische Quelle liegen im Live-Adapter.
4. F3- und S1-B-Anheftung sind Referenzoperationen und muessen sichtbar von
   der neutralen aktuellen Feldkonstruktion getrennt bleiben.
5. Ein sofortiges Verkleinern von `__init__.py` waere wegen bestehender
   Importnutzer unnoetig riskant. Zuerst ist eine kompatible neue Sollgrenze
   erforderlich.

## Gebundene Solloberflaeche

Eine spaetere kuratierte aktuelle API darf nur folgende Rollen anbieten:

```text
kontrollierte Audio-/Video-/Browserquelle
Rezeptorzustand und Rezeptorvertrag
Verteilung und Dockanatomie
atomare Zeit- und Ereignisuebergabe
gemeinsamer neutraler Feldzustand
kontrollierte Feldsitzung
Snapshot und Restore
explizit benannter optionaler F3-Referenzarm
```

Runner, Forschungspreregistrierungen, Kandidaten, Live-Geraete und physische
Effektoren werden nicht aus dieser Solloberflaeche reexportiert.

## Aussagegrenze

W2-A ist ein statischer Architekturaudit. Er veraendert keine API und belegt
keine Feldfunktion, kein Memory, Lernen, Feldzeit, Organisation, Semantik,
Selbstregulation oder KI. Es gab keinen Browserstart, keine Tests und keinen
Forschungslauf. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W2-B fuehrt die kleinste kompatible Codebereinigung durch:

1. `AudioFrameSource` und `SyntheticAudioFrameSource` werden in ein
   geraeteneutrales kontrolliertes Audioquellenmodul verschoben.
2. `live_audio_adapter` reexportiert beide Namen vorerst kompatibel.
3. `broadband_hearing_path` und `audio_video_neutral_field_runtime` importieren
   nur noch aus dem geraeteneutralen Modul.
4. Importidentitaet, synthetischer Audiopfad und bestehende Paketimporte werden
   fokussiert getestet.

W2-B veraendert keine Feldgleichung, keine Sensorfreigabe und keine
Root-Reexportmenge. Erst nach dieser Abhaengigkeitstrennung wird eine neue
kuratierte `current_api`-Oberflaeche vorbereitet.

## Spaeterer Umsetzungsstand W2-B

W2-B ist inzwischen mit einer geraeteneutralen Grenze aus gemeinsamem
Fehlertyp, Quellenprotokoll und synthetischer Quelle umgesetzt. Bestehende
Root- und Live-Adapter-Namen bleiben identisch. Der fokussierte Verbund
besteht mit `79 passed` und 18 Subtests. Naechster Schritt ist W2-C: eine
additive kuratierte `current_api`, ohne die bestehende Root-API zu verkleinern.
