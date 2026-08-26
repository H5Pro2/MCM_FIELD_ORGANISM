# W2-B: Implementierung der geraeteneutralen Audioquellengrenze

Stand: 2026-08-09

Entscheidung: `CONTROLLED_AUDIO_SOURCE_BOUNDARY_SPLIT_COMPATIBLY`

Formaler Forschungslauf: nein

## Ausgangspunkt

W2-A hat gezeigt, dass aktive kontrollierte Audiomodule ihr
`AudioFrameSource`-Protokoll und die synthetische Quelle aus dem inaktiven
`live_audio_adapter` beziehen. Die Root-Oberflaeche mischte dadurch
geraeteneutrale Testweltrollen mit echter Live-Geraeteanbindung.

## Umsetzung

Das neue Modul
`mcm_field_organism.controlled_audio_source` besitzt jetzt ausschliesslich:

- `AudioCaptureError` als gemeinsamen endlichen Quellenfehler;
- `AudioFrameSource` als geraeteneutrales Protokoll;
- `SyntheticAudioFrameSource` als deterministische kontrollierte Quelle.

Der Fehlervertrag musste gemeinsam mit Protokoll und Quelle verschoben
werden, weil die synthetische Quelle bei vorzeitigem Ende genau diesen
bestehenden Fehlertyp ausloest. Eine getrennte Fehlerklasse haette die
Kompatibilitaet gebrochen oder eine zyklische Abhaengigkeit erzeugt.

## Kompatibilitaet

`live_audio_adapter` importiert und reexportiert alle drei Namen weiterhin.
Damit bleiben exakt identisch:

```text
mcm_field_organism.AudioCaptureError
mcm_field_organism.SyntheticAudioFrameSource
mcm_field_organism.live_audio_adapter.AudioCaptureError
mcm_field_organism.live_audio_adapter.AudioFrameSource
mcm_field_organism.live_audio_adapter.SyntheticAudioFrameSource
```

Es wurde kein Root-Symbol entfernt oder hinzugefuegt.

Der technische Root-Postzustand lautet:

```text
Importmodule vor W2-B:       155
Importmodule nach W2-B:      156
eindeutige Root-Symbole:    1267
doppelte Root-Symbolnamen:     0
```

Das zusaetzliche Importmodul ist die neue geraeteneutrale Grenze. Die
operative Symbolzuordnung verschiebt dadurch `AudioCaptureError` aus der
Live- in die aktuelle kontrollierte Kategorie; die Root-Symbolmenge bleibt
gleich.

## Umgestellte Importnutzer

Folgende Module beziehen geraeteneutrale Rollen nun direkt aus der neuen
Grenze:

```text
audio_video_neutral_field_runtime
broadband_hearing_path
common_receptor_window
controlled_audio_phase_source
controlled_audio_video_test_world
finite_audio_video_field_run
public_av_container_source
receptor_time_alignment
```

Direkte Importe aus `live_audio_adapter` verbleiben nur dort, wo echte
Live-Rollen gebraucht oder kompatibel reexportiert werden:

```text
live_audio_video_field
mcm_field_organism.__init__
```

## Verhalten

Die synthetische Quelle behaelt:

- identische Float-Normalisierung der Frames;
- `overflow_count == 0`;
- monotonen `read_count`;
- identische Reihenfolge der Frames;
- denselben `AudioCaptureError` bei vorzeitigem Quellenende.

Es wurde keine Audioverarbeitung, Feldgleichung, Zeituebergabe oder
Sensorfreigabe veraendert.

## Verifikation

Geprueft wurden:

- exakte Klassenidentitaet zwischen neuer, alter und Root-Oberflaeche;
- gemeinsames Protokollobjekt in allen direkten Importnutzern;
- Verhalten und Fehlervertrag der synthetischen Quelle;
- finite Audioaufnahme und Breitband-Hoerpfad;
- kontrollierte Audio-Phasenquelle;
- neutrale AV-Feldruntime und finite AV-Feldstrecke;
- Rezeptorzeitabgleich;
- historischer oeffentlicher AV-Containeradapter.

Der fokussierte Verbund besteht mit:

```text
79 passed
18 subtests passed
27.30 s
```

Alle geaenderten Python-Dateien bestanden zusaetzlich `py_compile`.

## Aussagegrenze

W2-B ist eine kompatible Architektur- und Importbereinigung. Es gab keinen
Browserstart, keine Kamera, kein Live-Mikrofon, keine Feldmessung und keinen
Forschungslauf. Die Aenderung belegt kein Memory, Lernen, Feldzeit,
Organisation, Semantik, Selbstregulation oder KI. Lauf 197 bleibt
unberuehrt.

## Bester naechster Schritt

W2-C implementiert additiv ein kuratiertes Modul
`mcm_field_organism.current_api`. Es soll nur kontrollierte Quellen,
Rezeptorvertrag, Zeituebergabe, Verteilung, gemeinsames neutrales Feld,
Sitzung und Snapshot/Restore exportieren. F3 wird in einem sichtbar getrennten
Referenzabschnitt angeboten.

Die bestehende Root-API bleibt waehrend W2-C unveraendert. Ein fokussierter
Manifesttest bindet, dass Live-Sensorik, Z4, Runner, Effektoren und pausierte
Memory-/Materialkandidaten nicht in `current_api` gelangen.

## Spaeterer Umsetzungsstand W2-C

W2-C ist inzwischen additiv umgesetzt. `current_api` besitzt 114 neutrale
Kern- und 16 getrennte F3-Referenzexporte. Der fokussierte Verbund besteht mit
`65 passed` und 282 Subtests. Naechster Schritt ist W2-D: statischer Audit des
transitiven lokalen Importgraphen hinter der kuratierten Fassade.
