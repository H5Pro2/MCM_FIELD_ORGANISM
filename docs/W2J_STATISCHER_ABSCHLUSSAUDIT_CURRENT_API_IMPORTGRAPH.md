# W2-J: Statischer Abschlussaudit des current_api-Importgraphen

Stand: 2026-08-09

Entscheidung: `CURRENT_API_TRANSITIVE_CORE_CLEAN_FOUR_REFERENCES_ONLY`

Auditart: statisch

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Auftrag

W2-J verfolgt alle lokalen relativen Python-Importe hinter den direkten
Ursprungsmodulen der 126 `CURRENT_CONTROLLED_FIELD_EXPORTS`. Die 16 getrennten
`F3_REFERENCE_EXPORTS` sind nicht Ausgangspunkt dieses Kerngraphaudits.

## Graphinventar

```text
neutrale Manifestrollen:       126
direkte Kern-Ursprungsmodule:   29
transitiv erreichte Module:     36
lokale Importkanten:            95
```

Reproduzierbare Digests der sortierten statischen Mengen:

```text
Manifest SHA-256:
b92c93f5bcfacf09fd8cd0016807e7cb6cea09c9ffea1c4a7286a01fc6dc2d49

Graph SHA-256:
f136d4873717192dd9abe45d65e42638076eb94f56ea3be1efd866a75eaa01e7
```

## Direkte Ursprungsmodule

```text
architecture_contract
asynchronous_receptor_events
audio_video_field_geometry
audio_video_neutral_field_runtime
broadband_hearing_path
browser_payload_runtime
browser_payload_source
browser_receptor_bridge
browser_world_contract
controlled_audio_phase_source
controlled_audio_source
field_step_time
field_time_partition
finite_multimodal_field_run
finite_video_path
log_spectral_receptor
neutral_asynchronous_field_runtime
neutral_field_session
neutral_local_field_substrate
receptor_contract
receptor_distributor
receptor_process_contract
receptor_proposal_handoff
receptor_temporal_support
receptor_time_model
shared_field_session
shared_mcm_field
transient_dock_trajectory
transient_neuron_input
```

## Nur transitiv erreichte Module

```text
auditory_baselines
carrier_baselines
controlled_receptor_capture
mcm_local_development_state
mcm_neuron
mcm_neuron_layer
mcm_substrate_state
```

## Klassifikation

| Kategorie | Module | Ergebnis |
|---|---:|---|
| W2-A aktuelle kontrollierte Kernmodule | 26 | zulaessig |
| seit W2 neu getrennte neutrale Module | 6 | zulaessig |
| explizite Referenzmodule | 4 | zulaessig und sichtbar |
| historisch oder pausiert | 0 | kein Pfad |
| Live oder physisch inaktiv | 0 | kein Pfad |
| private Werkzeuge und Audits | 0 | kein Pfad |

Die sechs neuen neutralen Grenzmodule sind:

```text
architecture_contract
audio_video_field_geometry
controlled_audio_source
controlled_receptor_capture
receptor_proposal_handoff
receptor_time_model
```

## Zulaessige Referenzabhaengigkeiten

| Modul | Direkte Ursache | Rolle |
|---|---|---|
| `auditory_baselines` | `controlled_audio_phase_source` | technischer Audiokonfigurationsvertrag |
| `carrier_baselines` | `auditory_baselines`, `broadband_hearing_path`, `log_spectral_receptor` | gemeinsamer numerischer Validierungsfehler |
| `mcm_local_development_state` | `shared_mcm_field` | optionale S1-B-Referenzrolle im Snapshotschema |
| `mcm_substrate_state` | `shared_mcm_field` | optionale F3-M-Referenzrolle im Snapshotschema |

Diese Pfade aktivieren keine Referenzmechanik. Die beiden optionalen
Snapshotrollen dienen der verlustfreien Darstellung bereits vorhandener
Referenzzustaende.

## Geschlossene W2-D-Mischgrenzen

Die vier in W2-D erreichten Mischmodule sind im neutralen Graphen nicht mehr
vorhanden:

```text
receptor_time_alignment
receptor_proposal_handoff_audit
finite_audio_video_field_run
architecture_readiness
```

Ihre neutralen Anteile liegen jetzt in den sechs expliziten Grenzmodulen. Die
alten Module bleiben als kompatible Reexport-, Audit- oder Capturepfade im
Repository, ohne von `current_api` transitiv erreicht zu werden.

## Verwendete Quellen

- Python-AST von `mcm_field_organism/current_api.py`;
- Python-AST aller transitiv erreichten lokalen Module;
- W2-A-Modulklassifikation;
- W2-D-Ausgangsgraph und dessen vier Mischgrenzen;
- W2-E bis W2-I als dokumentierte kompatible Trennungen.

Es wurde kein Projektmodul importiert oder ausgefuehrt. Der Audit liest nur
statische Syntaxbaeume. W2-J fuehrt keine Tests oder Forschungslaeufe aus.

## Aussagegrenze

W2-J belegt die architektonische Trennung der kuratierten neutralen API. Er
belegt kein Memory, Lernen, Feldzeit, Organisation, Semantik,
Selbstregulation oder KI. Es wurde kein Browser gestartet und keine Kamera,
kein Live-Mikrofon oder andere physische Sensorik aktiviert. Lauf 197 bleibt
unberuehrt.

## Bester naechster Schritt

W3-A erstellt einen technischen End-to-End-Consumer-Test, der ausschliesslich
Namen aus `current_api` verwendet:

```text
synthetische kontrollierte Audio-/Videofolgen
-> Rezeptoren
-> kontrollierte Sequenzaufnahme
-> neutrales gemeinsames Feld
-> Snapshot
-> Restore
```

Der Test darf keine internen Modulimporte, keine Live-Geraete und keine
F3-Referenzaktivierung verwenden. Er prueft nur, ob die kuratierte Fassade als
eigenstaendiger technischer Entwicklungseinstieg vollstaendig ist; er ist
kein Forschungs- oder Memorynachweis.

## Spaeterer Umsetzungsstand W3-A

W3-A ist am 2026-08-09 umgesetzt worden. Ein technischer Consumertest nutzt
`current_api` als einzigen Projektimport und schliesst die kontrollierte
synthetische AV-Feld-Snapshot-Restore-Kette mit identischem Snapshot-Digest.
Der aktuelle Verbund besteht mit `118 passed` und 350 Subtests.
