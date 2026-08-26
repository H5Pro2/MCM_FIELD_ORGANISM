# S1-BD: Gemeinsame Zeit-, Handoff- und Feldgrenze

## Status

Statischer Architekturvertrag mit Regressionstest. Keine neue Feldmechanik,
kein Browserlauf, kein Forschungslauf und kein Memory-, Substrat- oder
KI-Befund.

## Frage

Erzeugen die synthetische AV-Zufuhr und die kontrollierte Browser-Testwelt
quellenspezifische Feldpfade, oder treffen beide vor dem gemeinsamen Feld auf
dieselbe neutrale Zeit- und Handoffgrenze?

## Befund

Beide Quellen erzeugen geordnete auditive und visuelle
`ReceptorTimeSequence`-Objekte mit expliziter technischer Uhr.

Die synthetische AV-Zufuhr verwendet:

```text
capture_audio_video_into_neutral_field
-> capture_timed_audio_video_receptor_sequences
-> advance_audio_video_receptor_sequences
```

Die Browser-Testwelt-Rezeptorbruecke verwendet:

```text
BrowserReceptorBridge.finalize
-> ReceptorTimeSequence (auditory, visual)
-> advance_audio_video_receptor_sequences
```

Ab `advance_audio_video_receptor_sequences` ist der Pfad identisch:

```text
gemeinsamer Feldschritthorizont
-> run_neutral_asynchronous_field
-> handoff_receptor_completion_groups
-> map_proposal_batch_to_transient_docks
-> project_transient_docks_to_neuron_inputs
-> neutrales gemeinsames S/H-Feld
```

Es existiert kein Browser-spezifischer Feldschritt, kein eigener Browserdock
und kein synthetik-spezifischer Handoff. Unterschiede vor der gemeinsamen
Grenze bleiben auf Quellenerfassung, Zeitstempelbildung und
Rezeptorreduktion beschraenkt.

## Dauerhafte Absicherung

Ein AST-Vertragstest bindet folgende Kette:

1. Die synthetische Capturefunktion ruft den gemeinsamen Sequenzeingang auf.
2. Der Browserpayload-Consumer importiert denselben Sequenzeingang aus der
   aktiven `current_api`.
3. Der Sequenzeingang ruft die neutrale asynchrone Feldruntime auf.
4. Die Feldruntime verwendet den gemeinsamen Handoff, die transienten Docks
   und die gemeinsame Neuroneneingabeprojektion.

Die bestehenden Consumer-Tests pruefen parallel beide realen kontrollierten
Datenpfade und deren Snapshot/Restore-Verhalten.

## Aussagegrenze

Die gemeinsame technische Kette belegt keine semantische multimodale Fusion,
keine psychologische Wahrnehmung, keine Praegung, keine Feldzeit und kein
MCM-Memory. Sie zeigt nur, dass Audio und Video unabhaengig von ihrer
kontrollierten Quelle dieselbe Feldarchitektur erreichen.

## Bester naechster Schritt

Die aktive Weltzufuhr ist nun bis zum gemeinsamen Feld architektonisch
vereinheitlicht. Als naechstes wird die Snapshotgrenze selbst geprueft: Ein
aktiver neutraler Snapshot darf keine C_i-, F3- oder S1B-Zustaende enthalten,
solange kein Referenzarm explizit zugeschaltet wurde.

