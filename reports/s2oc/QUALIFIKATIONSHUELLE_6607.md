# Prospektive OC-Qualifikationsbindung

Benutzerfreigabe vom 10.09.2026; Repository-Ausgangspunkt
`537109994cf777f8d36cda617aafe12226806c25` mit dokumentierten lokalen Änderungen.
Der aktuelle vollständige Quellenstand wird vor dem Test in `inventory.json`
und über dessen Digest in der Vorregistrierung gebunden.

Nur die lokale Qualifikationsgrenze steigt von 4.096 auf **6.607 Byte**.
Die enthaltene Reserve für den äußeren Prüfbeleg bleibt **768 Byte**;
für die gepackten Qualifikationsobjekte verbleiben 5.839 Byte.
Die bisher gemessenen **586 Byte Index-/ZIP-Metadaten** zählen zusätzlich
zur Metadatenklasse, nicht zur Qualifikationsklasse. Die bestehende maximale
Index-Metadatenreserve bleibt 2.048 Byte. Gemeinsam werden daher vorab
7.887 Byte Archiv und 768 Byte äußerer Prüfbeleg bilanziert.

Unverändert: 65.536 Byte Metadaten, 174.080 Byte Quellen,
262.144 Byte gemeinsame Zusatzhülle und Verifikation, 4.194.304 Byte gesamt,
512 Byte Berichtreserve und sämtliche nativen Einzelgrenzen. Die neue
Qualifikationsreserve wird nicht zusätzlich zu ihren physischen Anteilen
gezählt. Tatsächliche Originale bleiben bei fehlgeschlagener Verpackung
zusätzlich sichtbar; keine Kürzung oder Umklassifizierung.

`s2oc-shared-closure-qualification-20260910-02` bleibt ein Vorabstopp mit
null Testaufrufen. Die neue Ablage heißt
`s2oc-shared-closure-qualification-20260910-03`. Erst nach vollständiger
Vorbilanz dürfen die unveränderten 30 vorbereiteten Prüfgruppen genau einmal
starten. Die Gesamtbilanzen aller 22 Fortschrittspositionen und beider
Abschlussalternativen sowie die Qualifikationshülle werden vorher gespeichert.

Die vorhandene Fehlerhülle wird nicht verkleinert; die bestehende verlustfreie
Verpackung und ihre Entpackgrenzen bleiben identisch. Größere tatsächliche
Logs bleiben vollständig erhalten und können erneut eine Budgetverletzung
begründen. Diese Vorbindung garantiert nicht jeden denkbaren Fehler.

Keine historischen Passzahlen, kein Hauptlauf und keine neuen Quellen.
Gates nach Abschluss False. Frühere Dokumente und Fehlbefunde werden durch
diese ausdrückliche prospektive Änderung nicht umgedeutet.
