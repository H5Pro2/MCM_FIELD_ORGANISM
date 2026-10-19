# URA1: Abschluss des begrenzten Laufzeitoptimierungspakets

Stand 2026-10-15. **PASS_RUNTIME_PACKAGE; SERIES_TIME_NOT_READY.**
Vier fokussierte Testgruppen, beide bestehenden Kleinfallintegrationen und
**genau eine** vollständige nachgelagerte Prüfung des vorhandenen 1024-Frame-
Archivs bestanden. Keine Forschungsquellen, Bootstrapmatrix, Leistungswertung,
kein neuer Grössen-Policy-Lauf oder Forschungsversuch. Keine weitere Optimierungsserie.

## Umsetzung und Bindung

Neue Dateien, historische Dateien unverändert:

- tools/_s2uc_ura1_delta_fast_decode.py: eigenständige Decoderfassung, ohne Encoder-
  oder Policyimporte. Tabellenvalidierung und Deltaformat unverändert.
- tools/_s2uc_ura1_delta_fused.py: Paar-, Zielvollständigkeits- und Diagnoseprüfung
  gebündelt mit dem vollständigen kanonischen Envelope-Durchlauf.
- tools/s2uc_ura1_runtime_qualify.py: getrennte Test-, Kleinfall- und einmalige
  Archivprüfung unter dem harten gemeinsamen Windows-Job.
- tests/test_s2uc_ura1_delta_fast.py: unabhängiges Grössenorakel und Negativkontrollen.

Code, Runtime, Grenzen, Aufrufe, Entscheidungsvorlage und ursprüngliche Belege
wurden vor den Prüfungen in binding.json gebunden. SHA-256:
`4579c1a8967a9258c33b58d6e2f465f4e7e3b201def10b3d2314aa7a3f1e4689`. Nach Abschluss sämtliche Bindungsdateien erneut geprüft.
Der neue Archivprüfmarker archive/START.json ist verbraucht. Er erlaubt keine
Wiederholung und keinen Policy-Lauf. Die alten Grössenmarker bleiben unverändert.

Die kanonische Reihenfolge verlangt R vor U. R wird einmal für seinen Hashpräfix
und einmal gemeinsam mit U für den Paarvergleich gelesen, U nur einmal.
Dies ist bewusst kein behaupteter Einmalzugriff auf alle Daten: SHA-256 kann
nicht aus Teilhashes zusammengesetzt werden. Es gibt keinen Rohspool oder
Gesamthistoriencache. Prognosevergleich, Vollständigkeit und differences entstehen
im selben Prognosedurchlauf. Erfassungsanker werden weiter vor Encoderverarbeitung
gebildet und separat gespeichert. Der unabhängige Decoder verifiziert diese
Anker, den Strukturanker und den vollständigen Envelopehash eigenständig.

Die inkrementelle Grössenprüfung startet mit der validierten Anfangsgrösse.
Setzen ersetzt die Bytezahl des betroffenen Teilwerts; neue Objektmitglieder
zählen Schlüssel, Doppelpunkt und gegebenenfalls Komma mit. Löschen entfernt
dieselben Bestandteile. Stringspans korrigieren anhand der kanonischen Escapes
der ersetzten und neuen Zeichenabschnitte. Nicht-ASCII-Zeichen werden wie bisher
mit ensure_ascii=True dargestellt; UTF-8-Bytezahlen dieser kanonischen Darstellung
werden geprüft, keine rohe Zeichenanzahl. Nach jeder Operation gilt weiter
size+1 <=262144, einschliesslich später wieder verkleinerter Zwischenzustände.
Jeder fertige Record wird einmal vollständig serialisiert; seine tatsächliche
Länge muss zusätzlich der fortgeschriebenen Grösse entsprechen.

Teilwertserialisierungen bleiben nötig; es wird weder O(1)-Aufwand pro Operation
noch ein vollständig serialisierungsfreier Decoder behauptet. Die neue
Vergleichs-/Hashhilfszeit enthält per-Aufruf-Timer; Rekonstruktion und
Normalisierung stehen in der gemeinsamen Phasenzeit, nicht in diesen Untertimern.

## Abnahmeprüfungen

- **O01 PASS:** unabhängige vollständige JSON-Serialisierung nach jeder geprüften
  Operation als Grössenorakel; UTF-8/Unicode inklusive Emoji, JSON-Escapes,
  int/float/bool/null, negatives Null, neue/ersetzte/gelöschte Objektmitglieder,
  Listen, leere Container, Wurzelersetzung und Stringspans. Alte/neue Decoder-
  Ergebnisse und vollständig ausgegebene kanonische Bytes stimmen überein.
- **O02 PASS:** exakte Recordgrenze und ein zu grosser Zwischenzustand aus zwei
  einzeln zulässigen Werten, der in der nächsten Operation wieder schrumpfen
  würde. Beide Decoder brechen mit RECORD_LIMIT ab; übergrosse Anfangswerte
  mit INITIAL_SIZE. Kein Durchlassen aufgrund einer späteren Verkleinerung.
- **O03 PASS:** zwölf Manipulationsarten (fehlende/vertauschte Deltas, ungültige
  Pfad-/Wertreferenz, falscher Anfangswert, veränderter/ausserhalb liegender Span,
  Opcode, Envelopehash, Anker, Strukturanker, doppelte Objektschlüssel).
  Alter und neuer Decoder liefern jeweils denselben terminalen Fehlertext.
- **O04 PASS:** acht Frames, Envelopehash identisch zur bisherigen unabhängigen
  vollständigen Berechnung; R zweimal/U einmal je Folge. Zehn Negativkontrollen
  für Bestand, Zelle, Ticket, Original, Ziel, Prognosetermin, fehlendes Ereignis,
  Diagnose, Cleanup und zensiertes Ziel werden terminal erkannt.

Vier Testgruppen in 10,373 s; Testlog unter tests/tests.txt. Kein Testfehlschlag
oder Reparaturdurchlauf. Zwei bestehende 64-/48-Frame-Kleinfälle verwenden die
unveränderte Erfassung und unabhängigen Referenzen; kein neuer Handfall.
Beide Archive sind sogar **bytegleich gzip** mit den vorherigen Integrationsarchiven,
nicht nur in rekonstruiertem Inhalt und Ankern gleich.

D: 19728363 kanonische Byte, SHA-256
`abc86c2b96fddd529aa1101f7d7364063ca515be174e7b9dae97a77b426a7d78`.
Lebenszyklus: 13380342 Byte, SHA-256
`940b29d1f24deac9e1dfcf575234089ff6c78d29415aefce7972598fe66996cd`.
D je Arm 192 äussere/716 interne Ereignisse, 32 Prognosen, 31 Feedbackrecords;
Lebenszyklus 144/552, 24 Prognosen, 23 Feedbackrecords. Cleanup bestätigt.

## Genau eine grosse Archivprüfung

Nur das vorhandene Archiv wurde gelesen; keine Policies, Referenzengines oder
Quellengeneratoren erneut ausgeführt. Die ursprünglichen Referenznachweise bleiben
historische Belege; der neue Durchlauf bestätigt die gespeicherte Gleichheit,
Vollständigkeit, Diagnose und Integrität, nicht eine neue Policy-Ausführung.

Alle acht Anker stimmen exakt in Hash, Bytezahl und Anzahl mit dem alten
Decoderbeleg überein. Je Arm: 3072 äussere Ereignisse, 11276 interne Ereignisse,
512 Prognosen, 511 beobachtete Ziele; Ziel 1025 zensiert.
358862679 kanonische Byte, SHA-256
`6be2be3dfa6587565552a319d3c65379965d30378133d4d70cdd86402cae2f26`.
Dictionary 901970 Byte, Format 1029374 Byte, gzip 170176 Byte;
16357 Tabelleneinträge, 152878 Referenzkanten, 30742 Indizes. Unverändert.

## Gemessene Zeiten und Ressourcen

| Ausführung | Supervisor gesamt s | Gemeinsamer Kernel-Peak Byte | Workerexit / Ende |
|---|---:|---:|---|
| tests | 11.214 | 77512704 | 0 / bestätigt |
| small | 79.602 | 66822144 | 0 / bestätigt |
| archive | 262.136 | 81047552 | 0 / bestätigt |

| Phase | Sekunden | Worker-Lifetime-Peak Commit Byte am Phasenende | Python-Phasenpeak Byte |
|---|---:|---:|---:|
| D_hand_case_capture_references | 25.459 | 40148992 | 11185879 |
| D_hand_case_fused_pair_envelope | 16.240 | 40873984 | 11399034 |
| D_hand_case_encoding_output | 0.077 | 41226240 | 11624580 |
| D_hand_case_independent_decoder | 4.544 | 49692672 | 19770804 |
| D_hand_case_cleanup | 0.025 | 49692672 | 12180538 |
| lifecycle_trace_capture_references | 17.433 | 49692672 | 11734459 |
| lifecycle_trace_fused_pair_envelope | 10.856 | 49692672 | 11897009 |
| lifecycle_trace_encoding_output | 0.072 | 49692672 | 12143724 |
| lifecycle_trace_independent_decoder | 3.121 | 51494912 | 20296644 |
| lifecycle_trace_cleanup | 0.024 | 51494912 | 12549358 |
| archive_read_and_table_validation | 1.878 | 63152128 | 13827424 |
| archive_fused_pair_envelope | 177.403 | 65757184 | 14415049 |
| archive_independent_decoder | 82.408 | 65757184 | 13844654 |
| archive_cleanup | 0.092 | 65757184 | 12114422 |

Die Lifetime-Peaks in dieser Tabelle sind keine isolierten Phasenpeaks;
phasenbezogene private Samples stehen in den jeweiligen supervisor.json.
Kernel-Peaks erfassen den gemeinsamen Job; Pythontraces sind zusätzliche
Messinstrumentierung. Alle drei Prüfungen: 512-MiB-Hartgrenze eingehalten,
gleicher Job verifiziert, höchstens Supervisor plus ein Worker, Workerende
bestätigt, keine Partialdateien. Kleinfallstore explizit geschlossen und geleert;
Archivzustände freigegeben und gc.collect ausgeführt. Keine Kopie des grossen
Archivs im Export. Export-/Verwaltungs-/Vorbereitungsgrenzen unverändert,
Endbilanz in closure.json. Die drei Supervisorzeiten zusammen betragen
352.952 s; dies ist keine Forschungsserie.

Zeitvergleich: grosse unabhängige Dekodierung vorher 329.786 s, jetzt
82.408 s, beobachteter Faktor 4.002. Tracemalloc war
in beiden Messungen aktiv, Supervisorintervall jeweils 20 ms. Neu handelt es
sich um einen separaten Archivprozess ohne zuvor lebenden Encoderstore;
Hostlast/Allocatorzustand sind nicht kontrolliert. Kein statistisch abgesicherter
Beschleunigungsfaktor und keine daraus abgeleitete Erfassungseinsparung.

Kleine Decoder: D vorher 17,613 s, jetzt 4.544 s;
Lebenszyklus vorher 11,475 s, jetzt 3.121 s.
Der frühere Kleinfall-Supervisor sampelte 10 ms, der neue 20 ms; beide mit
tracemalloc und unveränderter Ereignisprofilierung bei der Erfassung.
Vorherige Kleinfallkodierung nutzte vorbekannte Envelopewerte; jetzt ist deren
Berechnung enthalten. Daher keine pauschale End-to-End-Prozentersparnis daraus.

Die grosse gebündelte Nachverarbeitung von 177,403 s benutzt den neuen Decoder
als Recordlieferanten. Die lebende Kleinfallverarbeitung benutzt dagegen den
unveränderten Encoderiterator samt Kopien und Normalisierung. Diese Werte sind
nicht ohne Weiteres auf eine neue grosse Live-Erfassung übertragbar. Hash-Update-
Untertimer gross: 1,107 s, Vergleichsuntertimer 0,181 s; beide bereits in der
177,403-s-Phase enthalten, nicht zusätzliche oder vollständige Prüflaufzeiten.

## Eine aktualisierte Serienmachbarkeitsbewertung

**Weiterhin SERIES_TIME_NOT_READY.** Die Stunde gilt für alle 32 Fälle und
sämtliche Serienarbeiten zusammen, einschliesslich unabhängiger Archivprüfung.
Keine Teilstarts, Auslagerung ungezählter Prüfkosten oder Budgetänderung.

Transparente konservative Planungsabschätzung, keine Serienmessung:

- Erfassungsansatz 640.984 s/Fall aus der alten Messphase unverändert
  beibehalten. Darin sind alte Paarprüfungen enthalten; ihre Kosten werden
  nicht als bewiesene Einsparung abgezogen. Das ist bewusst konservativ.
- Gebündelte Nachverarbeitung 259.838 s/Fall: grösserer Wert aus gemessener
  grosser Archivphase und 16-facher D-Kleinfallphase mit lebendem Encoderiterator.
- Ausgabe 1.231 s/Fall: lineare Abschätzung aus D-Kleinfalldateiausgabe.
- Unabhängiger Decoder 82.408 s/Fall gemessen am vorhandenen grossen Archiv.
- Start/Cleanup pauschal 2.314 s/Fall als Planungsansatz.

Zusammen 986.776 s/Fall ×32 = 31576.839 s (8.77 h).
Explizite **25 Prozent Unsicherheitsreserve**: 7894.210 s; damit
**39471.048 s (10.96 h) + M**. M bezeichnet zusätzlich die noch
ungemessene unabhängige Quellenprüfung, Bootstrap-/Statistikprüfung,
Serienverwaltung und Abschlussarbeiten; M wird nicht als null angenommen.
Die Reserve ist ein transparenter Planungsaufschlag, kein Konfidenzintervall
und keine garantierte Schranke für nichtrepetitive Quellen.

Die Planungslücke gegenüber 3600 s beträgt damit mindestens 35871.048 s
plus M. Schon 32-mal die neue Decoderzeit beansprucht 2637.065 s;
mit 25 Prozent Reserve verbleiben bei M=0 nur etwa
7.592 s je Fall für sämtliche anderen Arbeiten.
Die vorhandenen Erfassungsbelege stützen das nicht. Auch diese untere
Kostenbetrachtung ist eine Gleichkostenabschätzung, kein universeller Beweis
über unbekannte Geschichten.

Offen bleiben weniger repetitive Deltas, tatsächliche grosse Live-Verarbeitung,
Hostlast, vollständiger Serienexport/-speicher sowie Quellen-, Statistik- und
Vorstartqualifikation. Einzelfall- und Codec-Erfolge ersetzen diese Belege nicht.

Das begrenzte Paket ist abgeschlossen. Nächster Schritt beim Projektleiter:
diesen Fortschritt und die verbleibende globale Zeitlücke bewerten und vor
weiterer Forschungsplanung eine ausdrückliche Entscheidung zum künftigen
Zeitvertrag treffen. Keine automatische Budgeterhöhung, keine nachträgliche
Lockerung verbrauchter Versuche und keine weitere Optimierungsserie durch
Fortsetzung dieses Pakets.
