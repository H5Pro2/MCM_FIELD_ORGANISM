# Privater Decoderanschluss v3

## Abschluss: Anschluss qualifiziert, reale Metadatenhülle noch zu groß

`media-worker-qualification-20260911-01`: **QUALIFIED**, genau ein Aufruf,
14/14 bestanden in 84,258 Sekunden. Die vorherigen Vorabstopps bleiben
unverändert; keine historische Testserie wiederholt. Alle elf gebundenen
Quelldateien sind nach dem Test unverändert, Gates False.

| Belegklasse | Vorbindung Qualifikation | Ist einschließlich Restreserve | Grenze |
|---|---:|---:|---:|
| Quellen | 225.328 | 225.328 | 262.144 |
| Metadaten | 96.440 | 76.202 | 98.304 |
| Gemeinsame Zusatzhülle | 309.296 | 271.335 | 393.216 |
| Verifikation | 262.144 | 30.433 | 262.144 |
| Gesamt | 3.813.600 | 1.528.958 | 4.194.304 |

Die fünf Qualifikationsabschlussdateien belegen 9.878 Byte; Ressourcenbelege
und Zugriffsmarker 3.020 Byte. 8.094 Byte Restreserve sind in der Istbilanz
weiterhin enthalten. Physische Belege plus aktive externe Referenzen:
1.520.864 Byte. Zwölf getrennte neutrale 32-Byte-Dateien (384 Byte) sind
Prüfeingänge außerhalb dieser Belegablage; keine realen Medienpayloads.

Tatsächlich erreicht:
- Zugehörigkeit und aktive Jobgrenzen vor Öffnung neutraler Quellen;
  abgewiesene Einrichtung und fehlender Job ohne Quellenöffnung.
- Verweigerte Speicheranforderung samt `memory_limit_notification=true`;
  unveränderte 30-Sekunden-Frist mit `DECODER_TIMEOUT` und beendetem Worker.
- Native PyAV-Konversion künstlicher UHD-/Audioframes im begrenzten Prozess,
  ein Übergabeplatz, unveränderliche Rückgaben und abgewiesener Wiedereintritt.
- Eine vollständige native Sitzung über den Worker: 24 Ereignisse,
  20 Formationen, vier read-only Hinweise, 7.392 Feldkontakte, acht Scans;
  genau einmal unabhängig verifiziert, `RECORDING_COMPLETE`.
- `DECODER_CANCELLED` und `DECODER_WORKER_EXIT` jeweils nach einer Formation;
  ursprüngliche Feld-/Memorydigests erhalten, Sitzung CLOSED, keine zweite
  Veröffentlichung. Die Fehlerbelege wurden jeweils separat lesend geprüft.

Die native Konversionsprobe erreichte laut Jobzähler **514.392.064 Byte
Peak-Job-Commit** bei 536.870.912 Byte Grenze: nur 22.478.848 Byte Abstand
in dieser Probe. Das ist kein Nachweis, dass die ausgewählte MP4 hineinpasst.
Auch die konzeptionelle Unterteilung des Budgets in Bibliotheks- und
Frameanteile ist damit nicht empirisch bestätigt. Die Gesamtkappe wurde
geprüft; weder Quellen noch Faktor oder Grenze werden anhand des Peaks geändert.
`worker_closed` bezeichnet die bestätigte Prozessbeendigung; beim kontrollierten
Schließen wird der Job beendet, kein erfolgreicher FFmpeg-Flush behauptet.

### Vollständige konkrete Laufvorbereitung

Die unveränderte Quelle, Auswahl, 24 Ereignisse, Profile, Ressourcenprofil und
alle aktiven Quellen-/Qualifikationsreferenzen stehen nun in
[common.json](s2oe/media-run-binding-20260911-01/common.json).
Lauf-ID `media-memory-video-20260911-01`, Ergebnisverzeichnis weiterhin nicht
vorhanden. Die MP4 wurde für diese Bindung nicht geöffnet; der frühere
Dateihash ist als Herkunft gebunden und muss vor Verarbeitung erneut gelten.

[budget.json](s2oe/media-run-binding-20260911-01/budget.json) enthält alle
25 Fortschrittspositionen, beide Abschlussalternativen, Einzelklassen und
die vollständige Bilanz einschließlich sich selbst. Der Zugriff ist nur
eine Python-API; Browserplayer und autorisierter Starter fehlen weiterhin.

**Konkrete verbleibende Grenzverletzung:**

| Rechnung | Metadaten | Grenze | Überschreitung |
|---|---:|---:|---:|
| Unveränderte Startprüfung mit allen fünf aktuellen Qualifikationsabschlussdateien | 68.169 | 65.536 | 2.633 |
| Vollständige Bindung einschließlich Original-common und budget.json | 74.372 | 65.536 | 8.836 |

Die vollständige Rechnung bleibt bei Quellen 225.328, gemeinsamer Zusatzhülle
309.296 und Gesamt 3.758.177 Byte innerhalb der neuen Grenzen. Die eigenständige
Sitzungsmetadatengrenze wird dadurch nicht aufgehoben.

`common.json` belegt 8.964 Byte, `budget.json` 9.992 Byte. Die bestehende
Sitzung schreibt ihre eigene common-Kopie; Original und spätere Kopie sind
hier beide gezählt. Alle fünf aktuellen Qualifikationsabschlussdateien
(9.878 Byte) bleiben explizit referenziert. Die Startprüfung reserviert
zusätzlich weiterhin 8.704 Byte unter `@new-qualification-and-report`;
das ist eine zusätzliche Reserve, keine behauptete zweite physische Ablage
derselben Qualifikationsdateien. Die vollständige separate Rechnung zählt
statt dieser Zukunftsreserve die wirklichen Bindungsdateien und die
verbleibenden Abschlussreserven. Kein notwendiger Inhalt wurde entfernt.

Der Status der Laufvorbereitung ist daher **NOT_START_READY**, nicht eine
weitere Fehlqualifikation. Keine produktive Nachkorrektur nach dem bestandenen
Einmaltest. Die technische Workerqualifikation bleibt davon getrennt gültig.
Ein vorhandener neutraler Hilfsaufruf lehnte bei der administrativen Erstellung
zunächst eine vom Dateinamen abgeleitete ID ab; die tatsächliche Bindung wurde
mit der bereits festgelegten expliziten Lauf-ID erstellt. Dabei gab es weder
Quellenverarbeitung noch einen weiteren Qualifikationsaufruf.

### Integritätsbelege

- [Qualifikationsergebnis](s2oe/media-worker-qualification-20260911-01/result.json):
  `ba108c52ea6d030878165a4ceb53b34637e3798bc29f79de7c4ae4d9d866da4f`.
- [Quelleninventar](s2oe/media-worker-qualification-20260911-01/inventory.json):
  `77132692e36661481911c6c8a1ba527110cabd8b6de4b47ee335b160a7b35268`.
- [Istbilanz](s2oe/media-worker-qualification-20260911-01/final-balance.json):
  `9a0359b07c57776bcbb104c5326a1fd049ffe37b9f692872871a23e525ddf87e`.
- Lauf-common: `e009d3956b48336a1af09413c0676760fedec9d9d8c6a0a218e9f9de4c64aef9`.
- Laufbudget: `fd211426cbfd5896875ad559d762ba0e23d4e9d727a06b20f03546ed94bce44a`.

**RÜCKMELDUNG ERFORDERLICH:** Die vollständige reale Bindung verletzt die
unveränderte Metadatengrenze. Gemeinsame Referenzierung und verbleibende
Reservezuordnung müssen ausdrücklich entschieden werden; kein neuer
Quellen-/Memory- oder Decoderbudgetwechsel und kein Lernlauf gestartet.

## Prospektive Bindung vor dem Test

Die ausdrückliche Freigabe wird ausschließlich in
`s2oe.sampled-media.v3-decoder-job` umgesetzt: Quellen 262.144 Byte,
gemeinsame Zusatzhülle 393.216 Byte. Sitzungsmetadaten 65.536 Byte,
Gesamt 4.194.304 Byte und alle Memory-/Funktionsgrenzen bleiben unverändert.
Die gesamte Qualifikation bleibt bei 98.304 Byte Metadaten; diese größere
Hülle gilt weiterhin nicht für eine Sitzung. Historische Versionen und
Belege werden nicht umgedeutet. Die sieben v2-Quelldateien wurden vor den
Änderungen hashgeprüft unter `s2oe/qualified-v2-source-archive` erhalten.

Ressourcenprofil `s2oe.decoder-job.v1`: 512 MiB Prozess- und Job-Commit,
ein aktiver Prozess, ein 6.240.000-Byte-Ausgabeplatz, ein offener Auftrag,
4.096 Byte Antwortlimit, 30 Sekunden pro Anfrage, fünf Sekunden
Prozessbeendigung. Keine unbegrenzte Produktionswarteschlange.
Die Begründung des privaten Commitbudgets steht im vorherigen
`LOCAL_VIDEO_WORKER_PRECONDITION_20260911.md`; sie ist eine Betriebsgrenze,
keine Eignungsgarantie für jede UHD-Datei und keine Gesamt-RAM-Garantie.

Der Worker prüft seine Jobzugehörigkeit und die gesetzten Grenzen selbst vor
Medienimport/-öffnung. Feld, Memory und Rezeptoren bleiben im Elternprozess.
Die ursprüngliche Decoderkonversion bleibt erhalten; ihr Importpfad lädt im
Worker nun nur die leichten Fehler-/Zeithelfer, keine Memorymodule.
`stop()` kann den Job beenden, bevor es auf die Sitzungssperre wartet.
Bereits abgeschlossene Systemschritte werden nicht zurückgesetzt.

## Einmalige fokussierte Qualifikation

Vorgesehene ID: `media-worker-qualification-20260911-01`.
Dateigebundener Aufruf: `C:/Python314/python.exe -m reports.qualify_media_worker_once`
aus dem Projektverzeichnis `workspace`. Dies ist ausschließlich der neutrale
Qualifikationsaufrufer, kein Starter für einen realen Medienlauf.

Der Aufrufer bindet vor seinem einzigen Testprozess das vollständige aktuelle
Inventar aus elf Dateien, Umgebung, 14 neue Prüfgruppen, Ressourcenprofil,
alle 25 Fortschrittspositionen und alternative Erfolgs-/Fehlerhüllen.
Die historischen 14 Medientests werden nicht erneut ausgeführt.

Vollständige lokale Qualifikationsreserve: 14.336 Byte für Vorregistrierung,
vollständige Logs, Ergebnis und Istbilanz; weitere 512 Byte Berichtreserve.
Sechs mal 1.024 Byte werden gemeinsam für Ressourcenbelege und die kurzen
neutralen Zugriffsmarker reserviert. Diese Marker liegen innerhalb der
Qualifikationsablage und werden mitgezählt. Größere tatsächliche Fehlerlogs
werden nicht gekürzt, sondern als Überschreitung ausgewiesen.

Die Vorrechnung umfasst eine volle native Sitzung durch den Worker sowie
zwei Fehlerabschlüsse nach jeweils einer Formation, mit unveränderten
Maximalgrößen der nativen Belegklassen. Zusätzliche unabhängige Verifikation
ist mit 262.144 Byte reserviert. Die letzten Codeänderungen werden durch
die unmittelbar vor Aufruf erzeugte Vorregistrierung vollständig erfasst;
kein vorheriger Hash oder günstigerer Zwischenstand ersetzt diese Bindung.

Die neutrale Überlastprobe fordert mehr als das gesamte Job-Commitbudget
an und prüft Allocation-Denial samt Jobnachricht. Die Timeoutprobe wartet
tatsächlich auf die unveränderte 30-Sekunden-Frist. Native Framekonversion
erfolgt mit künstlichen Frames; vollständige Sitzungen verwenden einen
separaten, gebundenen neutralen Endpunktlieferanten im echten Jobprozess.
Kein MP4-Korpus und keine ausgewählte Benutzerdatei werden geöffnet.

## Verbleibende Aussagegrenzen

Nach abruptem Workerende sind die zuletzt quittierten Lesezähler ein
bestätigter Präfix; `read_counters_complete=False` kennzeichnet die fehlende
Vollständigkeit. Ein erfolgreicher Abschluss benötigt vollständige Zähler.
Der Verifikator prüft gespeicherte Job-/Quellenbindungen, kann die historische
OS-Durchsetzung aber nicht unabhängig aus einem JSON-Beleg rekonstruieren.

Die Summengrenzprobe der gemeinsamen Zusatzhülle ist ausdrücklich ein
arithmetischer Ledgertest mit bereits überschrittener Quellenklasse, kein
angeblich unter allen lokalen Limits erreichbarer nativer Beleg.

Browserplayer und versuchsspezifischer autorisierter Starter fehlen weiterhin.
Die Python-Sitzungs-API ist kein fertiger Benutzerzugang. Die konkrete reale
Laufbindung bleibt bis zum neuen Anschlussbefund gesperrt. Kein Lernlauf.

Dieses Dokument ist Arbeitsdokumentation außerhalb der Qualifikationsablage;
es ersetzt keinen Pflichtbeleg oder reservierten Abschluss darin. Wird es
später als notwendige Laufreferenz verwendet, ist seine Dateigröße mitzuzählen.
