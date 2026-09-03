# S2-KT Teilhinweisabruf 20260903-01

Lauf-ID: `s2ks-real-partial-cue-336-20260903-01`

Technischer Status: `NOT_EVALUABLE`

Funktionsstatus: keiner

Der genau einmal gestartete Hauptaufruf brach nach der Bildung der fuenf
frischen In-Memory-Geschichten beim ersten S2-KQ-Teilhinweis vor jeder
atomaren Ergebnisablage ab:

```text
S2KQ_SOURCE_INVALID: cue is stale or belongs to another clock
```

Das vorgesehene Laufverzeichnis wurde nicht erzeugt. Die genau einmal
ausgefuehrte unabhaengige read-only Verifikation meldete deshalb korrekt
`NOT_EVALUABLE` mit `atomic result directory differs`. Es existieren weder
Ergebnisdigest noch Funktionsauswertung. Der Lauf wird nicht wiederholt oder
nachtraeglich ergaenzt.

## Statische Ursachenlokalisierung

Der reale TSPM-Fast-Zustand bindet die nativen Rezeptoruhren getrennt als
`audio.sample` und `video.frame`. S2-KQ verlangt dagegen derzeit, dass
`auditory_source_clock_id`, `visual_source_clock_id` und die einzelne
`field_clock_id` des visuellen Teilhinweises identisch sind. Diese Bedingung
ist fuer den realen AV-Zustand nicht erfuellt und stoppt vor dem Slotscan.

Damit liegt ein technischer Integrationsfehler der Cue-Zeitbindung vor. Es
wurde kein Befund zu Trefferqualitaet, Mehrdeutigkeit oder Enthaltung
ermittelt. Memorykerne, Schwellen, Fixtures und S2-KQ-Entscheidungslogik
blieben unveraendert. Das Hauptgate war vor dem Aufruf `False` und nach dem
Abbruch wieder `False`.
