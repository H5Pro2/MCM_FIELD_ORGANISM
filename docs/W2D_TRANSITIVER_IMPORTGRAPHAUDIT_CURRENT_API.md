# W2-D: Transitiver Importgraphaudit der current_api

Stand: 2026-08-09

Entscheidung: `NO_HISTORICAL_TRANSITIVE_PATH_FOUR_MIXED_BOUNDARIES_REMAIN`

Auditart: statisch

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Auftrag

W2-D verfolgt alle lokalen relativen Python-Importe hinter den Ursprungsmodulen
der 114 `CURRENT_CONTROLLED_FIELD_EXPORTS`. Die 16 expliziten
`F3_REFERENCE_EXPORTS` sind nicht Ausgangspunkt dieses Kerngraphaudits.

## Graphinventar

```text
direkte Kern-Ursprungsmodule: 25
transitiv erreichte Module:    35
lokale Importkanten:           97
```

Alle 35 transitiv erreichten Module konnten genau einer W2-A-Kategorie
zugeordnet werden.

## Kategorien im transitiven Kern

| Kategorie | Module | Einordnung |
|---|---:|---|
| aktuelle kontrollierte Kernmodule | 27 | zulaessig |
| Referenzmodule | 4 | zulaessig, aber sichtbar zu begrenzen |
| private Durchleitungen | 3 | gemischte Modulgrenze |
| Live-/physisch inaktive Durchleitung | 1 | gemischte Modulgrenze |
| historisch oder pausiert | 0 | kein Leak |

Es gibt keinen transitiven Pfad zu Z4, Forschungsrunnern, Effektoren,
synaptischen Memorykandidaten, Kontaktmaterial, radialer Morphologie oder
anderen geschlossenen Substratfamilien.

## Zulaessige Referenzabhaengigkeiten

Vier Referenzmodule werden erreicht:

| Modul | Ursache im Kern | Rolle |
|---|---|---|
| `auditory_baselines` | `controlled_audio_phase_source` | technischer Audiokonfigurationsvertrag |
| `carrier_baselines` | `log_spectral_receptor`, `broadband_hearing_path` | gemeinsamer numerischer Validierungsfehler |
| `mcm_local_development_state` | `shared_mcm_field` | optionale S1-B-Referenzrolle im Snapshotschema |
| `mcm_substrate_state` | `shared_mcm_field` | optionale F3-M-Referenzrolle im Snapshotschema |

Diese Abhaengigkeiten aktivieren keine Referenzmechanik. Die letzten beiden
sind erforderlich, weil `SharedMCMFieldSnapshot` vorhandene optionale
Referenzzustaende verlustfrei darstellen und wiederherstellen kann.

## Gemischte Grenze 1: receptor_time_alignment

`receptor_time_alignment` ist in W2-A wegen seiner echten parallelen
Capture-Funktionen als `LIVE_OR_PHYSICAL_INACTIVE` klassifiziert. Acht
Kernmodule benoetigen daraus jedoch nur geraeteneutrale Zeitrollen oder eine
explizite kontrollierte Capture-Funktion:

```text
asynchronous_receptor_events
audio_video_neutral_field_runtime
browser_receptor_bridge
field_time_partition
neutral_asynchronous_field_runtime
neutral_field_session
receptor_temporal_support
transient_dock_trajectory
```

Die breiteste gemeinsame Abhaengigkeit liegt bei:

```text
OrganismTimedReceptorFrame
ReceptorTimeSequence
ReceptorTimeAlignmentError
```

Diese Rollen sind reine reduzierte Zeitmodelle. Sie benoetigen weder Kamera,
Mikrofon, Threadpool noch Capture-Clock. Ihre Lage im Capture-Modul ist daher
eine echte, kompatibel trennbare Architekturvermischung.

## Gemischte Grenze 2: receptor_proposal_handoff_audit

`neutral_asynchronous_field_runtime` und `transient_dock_trajectory` verwenden
aus diesem privaten Auditmodul operative Kernrollen:

```text
ReceptorProposalCompletionGroup
ReceptorProposalBatch
ReceptorProposalHandoff
handoff_receptor_completion_groups
```

Die passive Vergleichs- und Segmentierungsauswertung ist dagegen Auditwerkzeug.
Der heutige Modulname bildet diese Trennung nicht ab.

## Gemischte Grenze 3: finite_audio_video_field_run

`audio_video_neutral_field_runtime` importiert daraus nur:

```text
ORTHOGONAL_FIELD_SAMPLE_OFFSETS
audio_video_dock_anatomies
```

Beide Rollen beschreiben feste neutrale Geometrie. Das Ursprungsmodul enthaelt
zusaetzlich einen Capturelauf und Ergebnisrollen und ist deshalb als privates
Werkzeug klassifiziert. Die aktive Runtime benoetigt nicht dessen Capturepfad.

## Gemischte Grenze 4: architecture_readiness

`receptor_process_contract` verwendet nur:

```text
EvidenceLevel
RuntimePermission
```

Diese Enums sind Vertragsrollen. Das Ursprungsmodul enthaelt zugleich den
vollstaendigen passiven Architekturplan und bleibt deshalb private
Planungstechnik. Der Leak ist klein, aber real.

## Gesamtentscheidung

Die Exportfassade W2-C ist frei von verbotenen Namen und besitzt keinen
transitiven historischen oder pausierten Zweig. Vollstaendig schichtrein ist
der neutrale Kern dennoch nicht:

```text
4 zulaessige Referenzabhaengigkeiten
+ 4 gemischte Modulgrenzen
+ 0 historische/pausierte Leaks
```

Die gemischten Grenzen rechtfertigen keine Modulloeschung. Sie verlangen
kleine kompatible Extraktionen, bei denen alte Importpfade als Reexporte
erhalten bleiben.

## Verwendete Quellen

- Python-AST von `mcm_field_organism/current_api.py`;
- Python-AST aller transitiv erreichten lokalen Module;
- W2-A-Kategorien;
- konkrete Importrollen der vier gemischten Module.

Es wurde kein Modul importiert oder ausgefuehrt, um den Graphen zu erzeugen.
Der Audit liest ausschliesslich statische Syntaxbaeume.

## Aussagegrenze

W2-D ist ein statischer Architekturaudit. Er veraendert keinen Code, startet
keinen Browser und aktiviert keine Live-Sensorik. Er belegt kein Memory,
Lernen, Feldzeit, Organisation, Semantik, Selbstregulation oder KI. Lauf 197
bleibt unberuehrt.

## Bester naechster Schritt

W2-E extrahiert zuerst die geraeteneutralen Zeitmodellrollen
`ReceptorTimeAlignmentError`, `OrganismTimedReceptorFrame` und
`ReceptorTimeSequence` nach `receptor_time_model`.

Verbindlich:

1. `receptor_time_alignment` reexportiert die drei Namen kompatibel.
2. Alle geraeteneutralen Kernnutzer importieren direkt aus dem neuen Modell.
3. Capture- und Auditfunktionen bleiben unveraendert im bisherigen Modul.
4. Root- und bestehende Modulimporte behalten exakte Klassenidentitaet.
5. Manifest-, Zeitmodell-, Browserbruecken- und Feldsitzungstests muessen
   bestehen.

Erst danach werden Handoff, AV-Geometrie und Vertragsenums jeweils separat
bewertet.

## Spaeterer Umsetzungsstand W2-E

W2-E ist am 2026-08-09 kompatibel abgeschlossen worden. Die drei Zeitrollen
liegen jetzt in `receptor_time_model`; alte Importpfade reexportieren dieselben
Klassenobjekte. Im aktualisierten Kernimportgraphen mit 26 direkten
Ursprungsmodulen, 36 erreichten Modulen und 100 Kanten verbleibt nur die
kontrollierte Sequenzaufnahme als Abhaengigkeit auf
`receptor_time_alignment`. W2-F hat diese Funktion anschliessend kompatibel
nach `controlled_receptor_capture` verschoben. Der neutrale Kern erreicht das
Alignment-Auditmodul damit nicht mehr.
