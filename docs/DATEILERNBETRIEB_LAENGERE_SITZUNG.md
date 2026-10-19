# Endlicher Dateibetrieb mit erhaltener Sitzung

Auftrag `DATEILERNBETRIEB-LAENGERE-SITZUNG`, Stand 12.09.2026.
Statische Anschlussvorbereitung, keine Implementierung oder Ausführung.
Bezugscommit `537109994cf777f8d36cda617aafe12226806c25` plus vorhandener
Arbeitsbaum. Diagnosezweige bleiben geschlossen; kein Warten auf Anzeigefeedback.

## Kleinster vorgeschlagener Umfang

Dieselbe lokale Datei
`C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4`, einmal bis Quellenende.
Vorhandene Quellenbindung: 83.498.438 Byte, SHA-256
`df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
[Vorhandene Metadaten](../reports/LOCAL_VIDEO_ACCESS_20260911.md): Container
26.751.667 µs; 801 deklarierte Videoframes, 30000/1001 fps, Zeitbasis 1/30000;
Audio 48 kHz, Zeitbasis 1/48000, deklarierte Dauer 1.284.080 Ticks.
Hier nicht erneut auf Dateiinhalt oder Decoderzugang geprüft.

**20 vollständige AV-Formationen, keine Hinweise, kein zweiter Durchlauf.**
Auswahl n=0…19: Audiofenster `[1,4*n; 1,4*n+0,1)` Sekunden, also
0; 1,4; 2,8; …; 26,6 Sekunden. Native Audiostarts exakt `67200*n`,
je 4.800 Samples. Video: letzter Frame am oder vor `1,4*n+0,05` Sekunden,
mit tatsächlichem PTS, Zeitbasis und nachfolgendem Frame als Auswahlbeleg.
Keine inhaltsabhängige Auswahl. Das letzte Fenster endet bei 26,7 Sekunden;
danach beide Decoder bis EOF leeren, ohne weitere Formation.

Begründung: feste, gleichmäßige Abtastung nahezu der gesamten Zeitspanne
innerhalb der bestehenden 20-Formations-Grenze. Insgesamt nur zwei Sekunden
Audio und 20 Frames gehen an MCM. **Vollständiger Dateidurchlauf heißt nicht
vollständige Wahrnehmung aller Samples oder Bilder.** Zwischenbilder werden
dekodiert, aber nicht als zusätzliche Erfahrungen verwendet.

Eine Runtime, ein Materialisierer, ein Worker, ein Durchlauf, kein Reset.
Halbprofil, RGB-Konversion, Feldzweig und Memoryregeln bleiben unverändert.
Die bisherige Runtimezeit bleibt vorerst ordinalgebunden: 200-ms-Schritte,
letztes Fensterende bei 3,9 s. Medienzeit und Runtimezeit sind verschieden.
Der Vorschlag verlängert die beobachtete Dateizeit, **nicht die interne
Zeitachse oder die Zahl der Erfahrungen**. Fast-Ablauf bleibt an den bisherigen
Fortschreibungsregeln gebunden, nicht an Wartezeit oder 26,75 reale Sekunden.

## Bestehende Anschlüsse und notwendige Änderungen

| Anschluss | Vorhanden | Kleinste Änderung für diesen Modus |
| --- | --- | --- |
| Manifest / Auswahl | `_s2oe_media_binding.sequence`, `validate`, `selection_receipt` erzwingen genau zwei Zehnerdurchläufe und vier Hinweise. | Eigene private Modusversion für die genannte 20er-Folge; rationale Auswahlzeiten statt stiller neuer Bedeutung von `window_number/2`. Alte Version unverändert akzeptieren. |
| Zeit / Profile | `runtime_times` delegiert an OB; Original-PTS getrennt. UHD-Profil bindet Konversion und Worker. | Neue Quellen-/Code-/Auswahlbindung; Runtimezeit nicht neu skalieren. Native 30000/1001 nicht als 30 fps ausgeben. |
| Decoder | `_s2oe_media_decoder.begin/select/_select_audio` behalten sequenzielle Iteratoren, verlangen jedoch zwei Durchläufe, zehn Fenster und `window*24000`. | Einen vollständigen Durchlauf mit explizitem Samplebeginn/Frame-Auswahlzeit zulassen. Eng begrenztes EOF-Drain ohne Rezeptoraufruf ergänzen. Keine neue Decoderplattform. |
| Worker | `_s2oe_decoder_worker.WorkerDecoder` kapselt Decoder, Joblimit, einen Ausgabeslot und Abbruch. | Auswahlparameter und EOF-Abschluss durch denselben geprüften RPC-Pfad führen; Stopp auch im Drain prüfen. |
| Sitzung | `_s2oe_media_session.Session.process/next/close/bind_common` enthält mehrere feste 24er-Prüfungen. | Nur für neue Modusbindung tatsächliche Manifestlänge verwenden; Abschluss zusätzlich an beide EOF-Belege binden. Eine Runtime bleibt erhalten. |
| Player | `_s2oe_local_player.Player._run/status/stop` ist bereits ereignisweise; Starter vorhanden. | Gesamtzahl, Auswahlzeit und Vorschaugrenze aus Bindung lesen. Nach letzter Formation EOF-Drain, dann einmal schließen. Kein neuer Startermechanismus. |
| Belegprüfung | `_s2oe_media_verification.verify_record` prüft feste 24/44/22-Zähler und 7.392 Kontakte; Vorbilanz erzeugt 25 Fortschrittspositionen. | Neue 20er-Bindung: Positionen 0…20, 20/40/20-Zähler, 6.720 Kontakte, null Scans; EOF und getrennte Decoderzähler prüfen. Keine historischen Prüfungen lockern. |

Dateien liegen unter `tools/`; vorhandene Vorbilanz:
`reports/prepare_direct_media_budget.py`. Lauf- und Quellenzulassung müssen
den dann tatsächlichen Code einschließlich aktueller HTML-Datei binden.
Alte Qualifikationen sind keine pauschale Zulassung dieser Änderungen.

## Welche Grenzen welchen Zweck haben

- **Versuchsvorgaben:** exakt 24 Ereignisse, zwei Durchläufe, zehn Fenster,
  0,5-s-Raster, vier Hinweise, Fünf-Sekunden-Vorschau. Keine Memorykapazitäten.
- **Echte Betriebsgrenzen:** OB maximal 28 Ereignisse, 20 Formationen,
  Einzelbelege und Gesamthülle; Decoderpaket-/Framezähler, Lesevolumen,
  Job-/Puffergrößen, RPC-Timeout und Abbruchfrist. Nicht ersatzlos entfernen.
- **Integrität:** Reihenfolge, einzigartige IDs, monotone native PTS,
  Quellenhash, vollständige Modalitätsfenster, atomare Fortschreibung,
  Generationswechsel und einmaliger Abschluss. Unverändert erforderlich.
- **Memory:** begrenzte B4-/Fast-/Slow-Bänke und gesättigte Supports bleiben
  unverändert. Der Runtimekern `build_minimal_runtime_config` hat zwar keinen
  fest eingebauten 24er-Wert; das hebt die qualifizierten Aufruferlimits nicht auf.

## Ressourcenmodell

| Größe | Vorschlag / unveränderte Grenze |
| --- | --- |
| Runtimeereignisse / Formationen | 20 / 20, unter 28 / 20 |
| Audio / NJ / Visual | jeweils 20; 40 übergebene Modalitätspayloads |
| Feldkontakte / Scans | 6.720 / 0 |
| Zustandsbelege | höchstens 21 einschließlich Anfang, je 98.304 Byte |
| Eingänge / Schritthüllen | je höchstens 20 × 16.384 Byte |
| NJ / Formation / Generation | 20 × 1.024 / 20 × 1.536 / 20 × 1.536 Byte |
| Ausgewählte Rohpayloads | je 19.200 Byte PCM + 6.220.800 Byte RGB; nur schrittweise |
| Worker-Ausgabeslot / Queue | 6.240.000 Byte / 1, unverändert |
| Workerprozess und Job | jeweils 1.073.741.824 Byte im bestehenden dateigebundenen UHD-Profil; ein Prozess, ein Videodecoderthread |
| Einzelleseaufruf / Paketgröße | höchstens 1.048.576 / 4.194.304 Byte, unverändert |
| Containerlesegrenze | `12 * Dateigröße`, unverändert; Hashlesungen im Decoder werden mitgezählt |
| RPC / Worker-Stopp | 30 s / 5 s, unverändert; Überschreitung führt zum Fehler, nicht zum automatischen Wechsel |
| Laufmetadaten / Quellen / gemeinsame Zusatzhülle | bestehende Medienversion: 131.072 / 327.680 / 393.216 Byte |
| Verifikation / Gesamt | 262.144 / 4.194.304 Byte |

Die gemeinsame Zusatzhülle enthält Quellen + NJ + Formationen + Generationen.
Bei vollen Reserven dieser 20 Formationen können Quellen darin höchstens
311.296 Byte belegen, auch wenn ihre lokale Obergrenze höher ist. Lokale Maxima
sind keine gleichzeitig garantierte Reservierung. Hinzu kommen sämtliche
aktiven Referenzen, Zulassung, Qualifikation, Anzeige, EOF-, Fehler- und
Abschlussbelege in ihren bestehenden Klassen. Keine Auslagerung notwendiger
Dateien aus der Bilanz. Erfolgs- und Fehlerabschluss sind Alternativen;
physisch mehrfach gespeicherte Inhalte bleiben mehrfach gezählt.

**Decoderkonflikt:** `_frames` begrenzt derzeit Video auf 400 und Audio auf
600 Frames, Pakete insgesamt auf 2.048. Schon die 801 deklarierten Videoframes
passen nicht. Eine dünnere MCM-Abtastung behebt das beim sequenziellen Dekodieren
nicht. Für die neue Version vorgeschlagen, aber hier nicht geändert:
**1.024 Video-, 2.048 Audioframes und 4.096 Pakete**, einschließlich Flush.
Das ist eine ausdrückliche Änderung endlicher Decoderarbeitsbudgets,
keine Erhöhung der Memory-/Ereigniskapazität. Zahlen sind feste Schutzdeckel,
keine Behauptung gemessener Voll-Datei-Zähler. Unerwartet höhere Werte stoppen
den späteren Lauf; keine adaptive Erhöhung. Die genaue Paket-/Paddingfolge der
vollständigen Datei ist noch nicht beobachtet.

Der Decoder darf nach der Auswahl alte Frames verwerfen; bei EOF-Drain keine
RGB-Ausgaben sammeln. Der vorhandene Decoder konvertiert auch übersprungene
Frames zu RGB. Das ist CPU-Aufwand, aber keine Rezeptoranalyse; für den
kleinsten Anschluss keine zusätzliche Konversionsoptimierung beginnen.
Der Parent hält weiterhin endlich höchstens 20 Eingangs-/Schrittbelege und
21 Zustandsbelege. Kein unbegrenztes Snapshotjournal, keine Rohdatenablage.
Native Codec-Referenzpuffer fallen unter das Worker-Joblimit. Dieses begrenzt
**nicht** den Parent: serialisierte Byteobergrenzen beweisen keinen exakten
Python-Heap-Peak. Ein eigener harter Parent-Prozessspeicherdeckel ist nicht
vorhanden; diese Grenze bleibt offen, statt eine RAM-Garantie zu behaupten.
30-s-RPCs sind ebenfalls kein harter Gesamtwallclock-Deckel für alle nativen
Memory-/Serialisierungsschritte. Endliche Ereignis-/Operationsgrenzen bleiben
maßgeblich; keine Echtzeit- oder sofortige Stoppgarantie ableiten.

## Bedienung und Abschluss

Start: gebundene Datei, aktuelle Zulassung, Code und Budget prüfen, dann eine
Sitzung öffnen. Der Worker bestätigt den Dateihash vor Dekodierung.
Status: ausgewähltes/abgeschlossenes Ereignis, tatsächliche native Medienzeit,
Runtimezeit sowie Decoderpakete/-frames/-samples getrennt zeigen. Auswahlende
ist noch nicht EOF. Vorschau bleibt ausdrücklich unabhängig, während Verarbeitung
wie bisher inaktiv; keine synchronisierte Livewahrnehmung behaupten.

Nach Formation 20: `DRAINING` bis beide Streams regulär EOF melden. Tatsächlich
dekodiertes Padding und letzter nativer Endpunkt separat dokumentieren;
Containerdauer nicht als beobachteten Endpunkt ausgeben. EOF vor einem noch
benötigten Fenster bleibt technischer Abbruch. Danach automatisch einmal
schließen und einmal unabhängig prüfen. Benutzer-Stopp bleibt unvollständiger
Abschluss; Primärfehler nicht durch `CLOSE/INCOMPLETE` ersetzen. Bereits gültige
Feldwirkungen und Memorytransaktionen bleiben erhalten. Keine Wiederaufnahme.

Die Anzeige übernimmt aktuelle Transaktionsaktionen, Support, Slot und
Generation: entstanden, fortgeschrieben, ersetzt oder frei. „Stabil“ nur nach
vorhandener Regel. Keine neuen Abrufproben aus einer Statusabfrage; ohne
Hinweis heißt es „Abruf nicht angefordert“. Kein Wiedererkennungs-, Identitäts-
oder Sequenzlernversprechen aus längerer Dateidauer.

## Vor einer Implementierung verbindlich offen

Die 20er-Abtastung benötigt keine Kernlimiterhöhung. Ein vollständiger
Dateidurchlauf ist unter den **heutigen Decoderzählern nicht abgesichert**.
Die vorgeschlagenen drei Decoderdeckel und der neue EOF-Abschluss gehören
deshalb ausdrücklich zur nächsten begrenzten Implementierungsentscheidung.
Aktive Dateigrößen und die genaue neue Qualifikations-/Fehlerhülle stehen erst
mit dem Anschlusscode fest. Vor einem Test sind alle 21 Fortschrittspositionen
und beide Abschlussalternativen vollständig zu bilanzieren; die passende alte
Istbilanz ist keine neue Obergrenze. Hier wurde keine Tragfähigkeit behauptet,
die von noch unbekannten Abschlussgrößen abhängt.

Keine Medienzugriffe, Imports der Projektmodule, Tests oder Simulationen.
Keine neue Lauf-ID, keine Implementierung oder Grenzänderung. Gates False.
Sitzungsübergreifendes Wiederladen, Aufmerksamkeit, Semantik und neue
Abrufregeln bleiben eigene, nicht begonnene Aufgaben.
