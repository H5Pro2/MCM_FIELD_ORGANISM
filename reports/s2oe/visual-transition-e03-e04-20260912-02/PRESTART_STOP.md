# Vorabstopp: historische Quellenstände fehlen am gebundenen Pfad

2026-09-12; Bezugscommit `537109994cf777f8d36cda617aafe12226806c25`.
Die vorbereitete Ablage ist **kein ausgeführter Diagnoselauf**. Es gibt
keinen Tabellenaufruf und keine verbrauchte Berechnungs-Claimdatei.

## Vorbereitete Korrektur

- Neuer Anschluss `tools/_s2oe_visual_diagnostic_reference.py` verwendet die
  vorhandene gemeinsame `unpack()`-Funktion: Dateiintegrität, alle Referenzen,
  verschachtelte OC- und Medieninventare, Auflösung, native Digestprüfung.
- Tabellenmodul und die 12/12-Qualifikation bleiben unverändert. Für den neuen
  Anschluss sind 13 fokussierte Kontrollen vorbereitet, **nicht ausgeführt**.
- Neue Fehlerbilanz zählt Fehlerdiagnostik und Abschlussbericht auch nach
  einer bereits gespeicherten Tabelle beziehungsweise Prüfung. Metadaten-,
  Tabellen- und Gesamtgrenzen bleiben unverändert.

Der einmal aufgerufene Vorbereitungsschritt
`python -m reports.diagnose_visual_transition_v2_once prepare` stoppte in
`prepare()` / `add()` mit `ReferenceError: PREPARE_REFERENCE_CHANGED`.
Die endgültige Quellen-/Budgetbindung wurde deshalb nicht veröffentlicht.
Es gibt **keine bestätigte vollständige Vorbilanz** dieses neuen Anschlusses.

## Konkrete Abweichungen

Die folgende Prüfung las nur die vorhandenen Dateien und ihre Hashes.
Sie wiederholte weder Vorbereitung, Qualifikation noch Diagnose.

| Datei | Historisch gebundene Bytes | Aktuelle Bytes |
| --- | ---: | ---: |
| `tools/_s2oe_media_decoder.py` | 9.560 | 10.022 |
| `tools/_s2oe_decoder_worker.py` | 22.928 | 23.481 |

Decoder historisch:
`76a5fc5a2964e55997598cac5523d5d5195a2f228abd2c4f776336e786db52be`

Decoder aktuell:
`c50fb5f93ae6d81e45f3d319aaa83a7d73a9bb6d74eb5dd90edb70d13bd4009b`

Worker historisch:
`834347e9e6aa1399a7d35907e5cb7fab5b5314da1ef2b408194e5dfe67eacd5a`

Worker aktuell:
`45fe5042f5d3215849f031170167ccd8a24cc930b9fbf2353ef0da9166a680c1`

Maßstab ist die unveränderte `common.json` des historischen Videolaufs.
Die historischen Dateien wurden nicht durch heutige Hashes ersetzt. Die
aktuellen Decoderdateien wurden in diesem Auftrag nicht geändert oder
ausgeführt. Dieser Befund besagt nicht, dass historische Rezeptorwerte
beschädigt sind; er betrifft die vollständige Quellenauflösung am aktuellen Pfad.

## Erreichte Arbeit und Grenze

Neue Qualifikationsaufrufe: **0**. Neue Tabellenberechnungen: **0**.
Unabhängige Diagnose-Belegprüfungen: **0**. Medien-, Rezeptor-, NJ-, Memory-,
Feld- und Abrufaufrufe: **0**. Gates False. Kein Retry.

Benötigt werden die beiden unveränderten historischen Quellstände als
digestgeprüfte verfügbare Herkunftsartefakte. Alternativ wäre ausdrücklich
zu entscheiden, wie diese rein historischen, hier nicht ausgeführten
Decoderabhängigkeiten von den aktiven Offline-Abhängigkeiten getrennt werden.
Ein aktueller Decoder darf nicht stillschweigend als historischer ausgegeben
werden. Keine automatische Lockerung oder weitere Ausführung.

Der frühere Diagnoseabbruch bleibt NOT_EVALUABLE. Die neue Anschlusskorrektur
ist vorbereitet, aber **nicht qualifiziert**. Die numerische Frage bleibt offen.
