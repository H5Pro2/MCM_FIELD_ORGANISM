# Einmalige Decoderdiagnose: Fehler im Videopaketdecoder

Qualifikation: `decoder-phase-neutral-20260911-02`, genau einmal **5/5**,
`QUALIFIED`. Diagnose: `decoder-first-window-diagnostic-20260911-02`,
genau einmal `select(1, 0)`. Anschließend genau eine unabhängige lesende
Belegprüfung: **EVIDENCE_VALID**, Diagnose selbst **NOT_EVALUABLE**.

## Korrektur und Bindung

Nur die neutrale Snapshot-Ersetzung umfasst nun auch `close()`. Alle
Assertions sind unverändert. Die Aufruf-/Verifikationsdateien referenzieren
die neue Ablage und Qualifikations-ID. Die alten drei Dateistände sind
zusätzlich im `source-archive` des ersten Befunds erhalten; dessen Ergebnis
bleibt `4/5 / NOT_QUALIFIED`. Kein historischer Testlauf wurde wiederholt.

Worker und Decoder bleiben gegenüber der vorigen Diagnosevorbereitung
unverändert, einschließlich 512-MiB-Commitlimit:

- Worker: `92d8b46e42fa556130c1f0d0ed94a1406e5b8287c2d5ac2b16f490b602175839`
- Decoder: `76a5fc5a2964e55997598cac5523d5d5195a2f228abd2c4f776336e786db52be`
- Neue Bindung: `96890aed744bb89fe6c5922deffe8ee1aaa78136c1a084c270cb3e26eff50e66`
- Diagnose: `82b1cd568a332dd617060a555c36b11ef6abc78acb017bf2b45bacf47452a87c`

Die unveränderte MP4 wurde nur für den freigegebenen Decoderaufruf geöffnet.
Vor Containerverarbeitung prüft der bestehende Quellenpfad Größe und SHA-256.
Medienzeit 0 bis 100 ms; Videoauswahl letzter Frame bis Mittelpunkt 50 ms;
native 30000/1001 fps und Zeitbasen unverändert. Das Fenster wurde nicht
vollständig geliefert. Kein Retry und keine Optimierung.

## Beobachteter Fehler

Letzte bestätigte Phase: **VIDEO**, Operation **packet_decode**, Sequenz 2.
Die ursprüngliche Ausnahme ist **av.error.InvalidDataError**, errno
**1094995529**, ursprünglicher Worker-Code `DECODER_WORKER_FAILED`.
Der Stack führt über `Packet.decode`, `VideoStream.decode`,
`CodecContext.decode`, `_send_packet_and_recv` zu `av.error.err_check`.
Damit ist die Fehlerweitergabe aus dem Videopaketdecoder belegt, nicht
aus der Audioanalyse oder RGB-Konvertierung dieses Aufrufs.

Separat gespeichert: `memory_limit_messages=[9]`, Limitmeldung true.
Der Elternanschluss klassifiziert deshalb außen weiterhin
`DECODER_MEMORY_LIMIT`, ohne den Originalfehler zu verlieren.

| Diagnosegröße | Beobachtung |
| --- | ---: |
| Prozess-/Job-Commitlimit, jeweils | 536.870.912 Byte |
| Peak Process Commit | 528.936.960 Byte |
| Peak Job Commit | 535.515.136 Byte |
| gezählte Pakete | 4 |
| gelieferte native Videoframes | 1 |
| Audioframes / ausgewählte AV-Fenster | 0 / 0 |
| zuletzt bestätigte Lesemenge | 171.256.136 Byte |

Die Peaks dieser Diagnose liegen unter dem Limit. Das widerlegt eine
verweigerte weitere Allokation nicht; ebenso beweist die Limitmeldung allein
nicht, dass gerade sie den `InvalidDataError` verursacht hat. Die Meldungen
werden kumuliert, nicht einzelnen Allokationen zeitlich zugeordnet.
Keine Zahl ersetzt nachträglich einen fehlenden Messwert des historischen Laufs.

`process_exit_before_cancel=null`: kein Exitcode vor dem kontrollierten
Abbruch beobachtet. Danach Worker geschlossen, Exitcode 1; dieser ist kein
unabhängiger Crashnachweis. Die Lesemenge bleibt bei finalem
`read_counters_complete=false` ein bestätigter Mindeststand.

## Konkrete verbleibende Evidenzlücke

Der Python-/PyAV-Fehlerpfad ist jetzt bekannt. Nicht bekannt sind die
konkrete native Fehlermeldung, eine eventuell verweigerte Allokation samt
angeforderter Größe und deren unmittelbarer Zusammenhang mit dem Decoderfehler.
Der Beleg trägt daher weder die Behauptung einer beschädigten MP4 noch eine
bestimmte Speicheroptimierung als nachgewiesene Lösung.

Die zuvor erkannte RGB-Konvertierung verworfener Zwischenframes bleibt ein
separater Optimierungskandidat, nicht die diagnostizierte Auslösestelle.
Eine Korrektur dieser Konvertierung allein ist aus dem neuen Befund nicht
begründbar. Für die nächste Entscheidung wäre die begrenzte native
Fehlerursache aus dem fehlgeschlagenen Paketaufruf erforderlich, nicht ein
erneuter vollständiger Lernlauf oder ein erhöhtes Speicherlimit.

## Abschluss und Ressourcen

Rezeptoren, NJ, Feld, Memory, Runtime: jeweils **0**. Keine Gates geöffnet.
Keine Rohbilder oder Samples gespeichert. Die unabhängige Prüfung hat
Quellen-/Codebindungen, Belegform, Limits und Zähler gelesen, aber weder
Medien wieder geöffnet noch Decoder oder numerische AV-Prüfung ausgeführt.

Vorbilanz 118.318 Byte einschließlich vollständiger Reserven. Ist vor
Verifikationsdatei und Bericht: 60.711 Byte einschließlich sechs aktiver
Dateien und historischer gemeinsamer Quellenbindung. Für Verifikation und
Bericht sind zusammen 16.384 Byte reserviert; keine Grenzerhöhung.

Der historische Lauf `media-memory-video-20260911-01` bleibt unverändert
`NOT_EVALUABLE`. Die Diagnose-ID ist verbraucht. **RÜCKMELDUNG ERFORDERLICH:**
Entscheidung über die verbleibende native Fehlerklärung; kein Folgeaufruf
oder Produktfix automatisch freigegeben.
