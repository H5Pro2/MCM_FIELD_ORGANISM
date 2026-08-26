# W2-E: Implementierung des geraeteneutralen Rezeptorzeitmodells

Stand: 2026-08-09

Entscheidung: `DEVICE_NEUTRAL_RECEPTOR_TIME_MODEL_SPLIT_COMPATIBLY`

Implementierung: ja

Formaler Forschungslauf: nein

## Auftrag

W2-E trennt die drei reduzierten Zeitrollen aus dem gemischten Capture- und
Auditmodul `receptor_time_alignment`:

```text
ReceptorTimeAlignmentError
OrganismTimedReceptorFrame
ReceptorTimeSequence
```

Die Rollen beschreiben ausschliesslich reduzierte Rezeptorzustaende auf einer
gemeinsamen Organismusuhr. Sie benoetigen keine Kamera, kein Mikrofon, keinen
Threadpool und keine Capture-Clock.

## Umsetzung

Das neue Modul `mcm_field_organism.receptor_time_model` ist die
geraeteneutrale Eigentumsgrenze der drei Rollen. Das bisherige Modul
`receptor_time_alignment` importiert und reexportiert sie weiterhin. Dadurch
bleiben bestehende Root- und Modulimporte kompatibel und objektidentisch.

Die folgenden aktiven Kernmodule importieren ihre Zeitrollen jetzt direkt aus
dem neuen Modell:

```text
asynchronous_receptor_events
audio_video_neutral_field_runtime
browser_receptor_bridge
field_time_partition
neutral_asynchronous_field_runtime
neutral_field_session
receptor_proposal_handoff_audit
receptor_temporal_support
transient_dock_trajectory
```

`current_api` exportiert die drei Rollen additiv als neutralen Kern. Ihre
Manifestgroesse steigt damit von 114 auf 117 neutrale Kernrollen. Die 16
getrennten F3-Referenzrollen bleiben unveraendert.

## Kompatibilitaet

Der fokussierte Identitaetstest belegt fuer jede der drei Rollen:

```text
receptor_time_model
is receptor_time_alignment
is Paket-Root
is current_api
```

Capture- und Auditrollen wurden nicht in das Zeitmodell aufgenommen. Das neue
Modul stellt insbesondere weder
`capture_timed_audio_video_receptor_sequences` noch
`capture_timed_audio_video_receptors` oder `ReceptorTimeAlignmentAudit`
bereit.

## Verifikation

```text
80 passed
301 subtests passed
Python-Kompilierung erfolgreich
117 neutrale Kernexporte
16 getrennte F3-Referenzexporte
133 eindeutige current_api-Exporte
```

Der aktualisierte statische Kernimportgraph umfasst:

```text
direkte Kern-Ursprungsmodule: 26
transitiv erreichte Module:    36
lokale Importkanten:          100
```

Die zusaetzlichen Zahlen entstehen durch die neue explizite Modellgrenze und
sind kein historischer oder pausierter Leak. Von den zuvor zehn direkten
Kernnutzern der Zeitrollen beziehungsweise Capture-Funktion importiert nur
noch `audio_video_neutral_field_runtime` aus `receptor_time_alignment`. Dieser
Import betrifft ausschliesslich
`capture_timed_audio_video_receptor_sequences`.

## Verwendete Quellen

- bestehende Rollen in `receptor_time_alignment`;
- direkte Importstellen der aktiven Kernmodule;
- `current_api`-Manifest;
- fokussierte Manifest-, Grenz-, Browserbruecken-, Zeit- und
  Feldsitzungstests;
- statischer Python-AST-Importgraph.

## Aussagegrenze

W2-E ist eine kompatible Architekturtrennung. Es wurde keine Testwelt
ausgefuehrt, kein Browser gestartet und keine Kamera, kein Live-Mikrofon oder
andere physische Sensorik aktiviert. Die Umsetzung belegt kein Memory,
Lernen, Feldzeit, Organisation, Semantik, Selbstregulation oder KI. Lauf 197
bleibt unberuehrt.

## Bester naechster Schritt

W2-F trennt die kontrollierte Sequenzaufnahme
`capture_timed_audio_video_receptor_sequences` aus
`receptor_time_alignment` in ein eigenes Modul
`controlled_receptor_capture`.

Verbindlich:

1. `receptor_time_alignment` reexportiert die Funktion kompatibel.
2. `audio_video_neutral_field_runtime` importiert sie direkt aus der neuen
   kontrollierten Capturegrenze.
3. Zeitmodell und Alignment-Audit bleiben unveraendert getrennt.
4. Bestehende Funktionsidentitaet und Verhaltenstests muessen bestehen.
5. Danach darf der neutrale Kern `receptor_time_alignment` nicht mehr
   transitiv erreichen.

## Spaeterer Umsetzungsstand W2-F

W2-F ist am 2026-08-09 kompatibel abgeschlossen worden. Die kontrollierte
Sequenzaufnahme liegt jetzt in `controlled_receptor_capture`. Der neutrale
Kern erreicht `receptor_time_alignment` nicht mehr. Alter Modulpfad,
Paket-Root und aktive Runtime behalten dasselbe Funktionsobjekt.
