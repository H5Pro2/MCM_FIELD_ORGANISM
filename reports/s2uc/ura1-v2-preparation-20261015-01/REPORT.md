# URA1 V2: vollständiger Vorbereitungsbericht

Stand 2026-10-15. **PASS_PREPARATION_V2 — separate Forschungsbeauftragung erforderlich.**
Neuer Gesamtzeitvertrag URA1_TIME_V2_57600. Acht Tests P01–P08, unabhängige
Quellenrezept-/Matrix-/Statistikprüfungen sowie Startfehler- und Watchdogproben
bestanden. Keine Forschungsquelle erzeugt oder gesichtet, keine Forschungsserie,
kein neuer 1024-Frame-Policy-Lauf. Keine weitere Optimierungsserie.

## Neuer Zeitvertrag

[Vertrag](../../../docs/S2UC_URA1_GESAMTZEITVERTRAG_V2_20261015.md): global
57600 Sekunden ab monotonem Supervisorbeginn vor Eintrittsprüfung bis nach
Abschlussmanifest. Workerfrist **54000 Sekunden ab demselben Beginn**, keine
neue Frist je Fall. Die letzten **3600 Sekunden** sind ausschliesslich für
Supervisorabschluss, Cleanup, Datei-/Bindungsbilanzen und Ergebnis-/Abbruchbericht
reserviert. Quellenprüfung, 64 Arme, Referenzen, alle Ereignisse, Archive,
unabhängige Archivprüfung und vollständig referenzgeprüfte Statistik müssen
innerhalb der Workerfrist fertig sein. Keine ungezählten Nacharbeiten/Teilstarts.

Der Supervisor beendet den Worker bei seiner Frist; der Ledger prüft zudem die
globale Frist in der Abschlussphase. Alle Budgetprüfungen sind kumulativ.
Fehler oder unvollständige Fälle bleiben TECHNICAL_ABORT/NICHT_AUSWERTBAR.
START verbraucht die Freigabe auch bei früher Quellen- oder Laufstörung.
Historische 3600/3540-s-Verträge und verbrauchte Marker bleiben unverändert.

## Implementierung

Neue Dateien:

- tools/_s2uc_ura1_v2_sources.py: festes Rezept, getrennte neutrale und gesperrte
  Forschungszugänge, eigene Zähler je Stream, Rejection Sampling, Ziehungsgrenze.
- tools/_s2uc_ura1_v2_source_reference.py: unabhängige Rekonstruktion ohne
  Produktionsgenerator oder Shuffle; gemeinsame Schnittstelle nur Zugangssperre.
- tools/_s2uc_ura1_v2_stats.py und _stats_reference.py: getrennte Matrixprüfung,
  rationale Mittelwerte, Paarbootstrap, Quantile und komplette Nebenbilanzen.
- tools/_s2uc_ura1_v2_series.py: kumulierte Ledgergrenzen, frische Arme pro Fall,
  Quellen-/Archiv-/Verwaltungskategorien, Vollständigkeit und Cleanup.
- tools/_s2uc_ura1_v2_engine.py: unveränderte Referenz-/Ereignisprüfungen des
  gebundenen Grösseneinstiegs, nur neue separate Datei und Auftragsrahmen.
- tools/_s2uc_ura1_v2_fused.py: bisherige gebündelte Prüfungen; neutral_only ist
  nun ausdrücklich boolesch und übernimmt die tatsächliche Quellenherkunft.
  Forschungsrecords werden nicht als neutrale Quellen ausgegeben.
- tools/s2uc_ura1_prepare_v2.py: Qualifikation und separat gesperrter späterer
  Forschungsaufruf, gemeinsamer Windows-Job, globaler Watchdog, Abschlussbindung.
- tests/test_s2uc_ura1_prepare_v2.py und neuer Vertragsstand.

Keine U/R-Regel, Deltaformat- oder Decoderänderung. R benutzt unverändert die
Originalrecency-Auswahl; unabhängige Referenzen und vollständige Bestands-/Zell-/
Ticket-/Hypothesen- und Ereignisprüfungen bleiben erhalten. Die MAE-Berechnung
bleibt im ursprünglichen binary64-Pfad; erst gespeicherte MAE werden rational
weiterverarbeitet. Kein FMA oder Reordering neu eingeführt.

## Quellenprüfung ohne Forschungsquellen

Geprüft wurden r=1 und r=2 ausschliesslich unter MCM-URA1/neutral/v1; beide
Orientierungen mit 256 Blöcken, 1024 Katalogindices und den festgelegten
Kontingenzen. Das ist eine Rezeptprüfung, kein 1024-Frame-Policy-Lauf.
Zusätzliche Handpermutation und künstliche Rejection-Samples prüfen Zurückweisung,
Zähler, getrennte Streams und die Grenze von 4096 Rohziehungen.

Der Forschungszugang scheitert vor der ersten Hashziehung ohne zulässiges Permit;
das ist im Test mit gesperrtem SHA-Aufruf nachgewiesen. Kein Forschungssource-
Namensraum wurde ausgewertet. Im später gesondert beauftragten Lauf werden alle
32 Quellen zuerst erzeugt, unabhängig überprüft und in sources-manifest.json
versiegelt, bevor irgendein Arm startet. Keine Auswahl oder Ersetzung nach
Policyergebnissen. Das Quellenmaterial wird nur über tatsächliche Vektoren
an die Arme übergeben; keine Cue-/Orientierungslabels im Policyeingang.

Die jetzige Bindung umfasst **Quellenrezept und gesperrten Erzeugungscode**;
Forschungsquellenbytes sind absichtlich noch unbekannt. Ihr Manifest entsteht
innerhalb des später ausdrücklich autorisierten Einmallaufs, vor allen Armen.
Dies ist kein bereits heute vorhandener Quellenhashnachweis.

## Matrix und rationale Statistik

Matrix: 320000 Byte; SHA-256
`0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965`.
10000 Zeilen mit je 16 Indices der ersten und 16 der zweiten Orientierung,
exakt nach MCM-URA1/bootstrap/v1. Unabhängige positionsweise Rekonstruktion
bestanden; eigene Bindung matrix-binding.json. Keine Forschungsquelle beteiligt.

Primär: D:U−R über alle 256 Q-Ziele je Geschichte und alle 32 Geschichten.
Rationale Mittelwerte und bootstrapweise Mittelwerte; Quantile 1/40 und 39/40
mit h=9999q und linearer Interpolation. Vorzeichen-/Nullgrenzen unverändert.
Sekundär Q, G_all, S, Q_X/Q_Y, jeweils gesamt und nach Orientierung deskriptiv;
U/R-Mittelwerte, Paarwerte, Gewinn/Schaden/Netto, besser/schlechter/gleich,
maximaler Schaden samt Positionen, schlechteste Geschichte und kumulierte
Zielunterschiede. Diagnosen: Hypothesenanzahl 0/1/mehrere, U-Kalt/Warm-Belegung,
gleiche Ausgabe, Persistenz/Kontext und gleiche/verschiedene Kontexte.
Keine zusätzlichen sekundären Erfolgsregeln oder Konfidenzintervalle eingeführt.

Die vollständige Aggregation und unabhängige Referenz wurden an **32 künstlichen
Zahlentabellen mit je 511 Zeilen** geprüft. Das waren keine Quellen, Geschichten
oder Policy-Läufe. Sämtliche Ergebnisfelder stimmen exakt überein; keine
wissenschaftliche U/R-Leistungswertung wird aus diesen Testzahlen abgeleitet.

## Test-IDs und Ergebnisse

- P01 PASS: gesperrter Forschungszugriff vor Hashziehung; zwei neutrale
  Rezeptrekonstruktionen; manipulierte Indices, Katalog, Zähler, Orientierung
  und Herkunft werden abgewiesen.
- P02 PASS: Handpermutation, Rejection Sampling, korrekte Zählung auch verworfener
  Ziehungen und terminale 4096-Grenze.
- P03 PASS: unabhängige Matrixprüfung, beschädigter Orientierungseintrag,
  rationale Quantilinterpolation, konstante negative/null/positive Intervalle.
- P04 PASS: vollständige Fall-/Zielmengen, Duplikate, Orientierung, Cue-Anzahlen,
  nichtendliche MAE und Diagnosebezeichnungen; fehlerhafte Tabellen abgewiesen.
- P05 PASS: kumulierte Verwaltungs- und Exportgrenzen, Workerfrist, globale
  Abschlussfrist sowie Entfernung temporärer Dateien bei Abbruch.
- P06 PASS: vollständige erwartete Fallzählung, Duplikate, Abbruch beim ersten
  fehlerhaften Cleanup; spätere Fälle werden nicht gestartet.
- P07 PASS: zwei reguläre Achtframefälle, vier unterschiedliche Armobjekte,
  identische Ergebnisse bei gleicher Eingabe nach Reset; beide Archive unabhängig
  geprüft. Zusätzlich absichtlich abgebrochener kurzer Referenzpfad, Arm-/Store-
  Cleanup bestätigt. Kein dritter vollständiger Policyfall.
- P08 PASS: Vorstart-/Runtime-/Grenz-/Aufrufprüfung, fehlende/falsche Berechtigung,
  exklusiver Zielordner. Berechtigungstests nur in temporären Testordnern.

8/8 Tests in 16,449 s. Zusätzlich reale Watchdogprobe: Worker nach 0,122 s
beendet; separater Startfehler korrekt erfasst. Keine erneuerte Einmalfreigabe.
Test-, Timeout- und Startfehlerprotokolle liegen in diesem Vorbereitungsordner.

## Messwerte und Planung

Vorbereitungsworker: 32.284 s, Supervisor: 32.913 s.
Gemeinsamer Kernel-Peak **78356480 Byte**, harter
512-MiB-Job, höchstens zwei Prozesse, gemeinsame Mitgliedschaft und Workerende
bestätigt. Der Job-Peak in anschliessenden Fehlerproben ist der kumulierte
Job-Peak, kein isolierter Peak der jeweiligen Probe. Tracemalloc war in dieser
Qualifikation aktiv, Supervisor-Samples alle 50 ms. Vergleiche zu früheren
20-ms-Messungen sind deshalb keine kontrollierten Beschleunigungsmessungen.

| Vorbereitungsphase | Sekunden | Python-Phasenpeak Byte |
|---|---:|---:|
| matrix_generation | 3.729941 | 453027 |
| matrix_independent_verification | 5.474049 | 465899 |
| neutral_sources_two_orientations | 0.053755 | 508289 |
| focused_tests | 16.451696 | 16580163 |
| artificial_statistics_input | 0.155559 | 8123211 |
| rational_statistics | 3.856101 | 12118342 |
| independent_statistics | 2.426285 | 15208897 |
| closure_serialization_and_hash | 0.097579 | 12068621 |
| cleanup | 0.033371 | 10370193 |

Statistikexport des künstlichen Vollschemas: 247004 Byte. Seine Serialisierung,
Hashbildung und JSON-Leseprüfung dauerten 0,098 s. Das ist nur ein Abschluss-
Teilkostenbeleg, kein Nachweis für alle künftigen Dateien und Datenträgerlatenzen.

Die bisherige konservative Kernplanung bleibt unverändert bei
39471.048 s für 32 Fälle **einschliesslich ihrer 25%-Unsicherheitsreserve**;
keine weitere Optimierungsannahme oder Erfassungseinsparung.
Neu gemessene und explizit budgetierte Zusatzarbeiten:

| Bestandteil | Messbezug | Planungsansatz |
|---|---|---:|
| Quellenprüfung/Versiegelung | 2 neutrale Orientierungen: 0.053755 s; lineare 32er-Schätzung 0.860078 s, ohne Serien-I/O | 120 s |
| Matrix-Reprüfung + Statistik/Referenz | 5.474 s + 6.282 s am künstlichen vollständigen Schema | 600 s |
| Eintrittsbindung und Serienverwaltung/I/O | noch nicht als Gesamtserie gemessen | 120 s |
| Supervisorabschluss | kleiner Serialisierungs-/Hashbeleg; volle Serie offen | 3600 s innerhalb Gesamtfrist |

Workerplanung **40311.048 s** gegenüber 54000 s.
Gesamtplanung **43911.048 s = 12.20 h** gegenüber 57600 s.
Verbleibender Puffer **13688.952 s = 3.80 h**.
Die 3600-s-Abschlussreserve ist dabei vollständig eingerechnet, kein zusätzliches
Budget ausserhalb der 16 Stunden. Die einmalige Matrixerzeugung ist bereits in
der Vorbereitung erfolgt; spätere Matrix-Reprüfung ist im 600-s-Ansatz enthalten.

**16 Stunden sind nach diesen konservativen Ansätzen plausibel, nicht garantiert.**
Es gibt heute keine rechnerische Zeitlücke. Offen bleiben nichtperiodische
Quellen, andere Delta-/Recordzahlen, künstliche statt reale Fehlerbruchwerte in
der Statistik, Rechnerlast und langsames I/O. 120/600/120 Sekunden sind bewusste
Planungsansätze mit Abstand zu den kleinen Messungen, keine gemessenen Obergrenzen.
Eine Überschreitung führt zum Abbruch, niemals zur eigenständigen Fristerhöhung.

Speicher-/Exportplanung: bislang höchster grosser technischer Job-Peak
146649088 Byte; neue Statistikqualifikation 78356480 Byte. Beide werden nicht
blind addiert oder mit 32 multipliziert: Fälle sind sequenziell, Stores werden
freigegeben; kompakte Fallstatistik bleibt kumuliert und ist noch kein gemessener
vollständiger Serienpeak. Gemeinsame 512 MiB bleiben hart. Grosse Dictionary-
und gzip-Werte des periodischen Belegs sind keine Schranke für neue Quellen.
32 × maximale 512-KiB-Archive =16 MiB, unter dem 32-MiB-Archivbudget;
32 × maximale 32-KiB-Quellen =1 MiB, unter 2 MiB. Vorbereitung <=8 MiB,
Verwaltung <=2 MiB, Abschluss <=1 MiB und Gesamtexport <=64 MiB bleiben separat
kumulativ geprüft. Ein real grösserer Statistikexport wird terminal abgewiesen.

## Vorstartbindung und nächster zulässiger Schritt

prestart.json und prestart.sha256 binden geprüften Code, Runtime samt DLLs,
Vertrag, Matrix, Prüfbelege und diesen Bericht. Der abschliessende SHA wird
in der Ergebnisübergabe genannt; kein selbstreferentieller Berichtshash.
Exakter späterer Aufruf:

`C:\Python314\python.exe -m tools.s2uc_ura1_prepare_v2 run C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-v2-preparation-20261015-01\prestart.json C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-v2-preparation-20261015-01\authorization.json`

Der Aufruf ist **nicht ausgeführt**. authorization.json existiert nicht;
Forschungszielordner und START existieren nicht. Separat erforderlich ist eine
Forschungsbeauftragung genau auf den neuen Vorstart-SHA; erst dann darf die
passende Berechtigung erstellt und genau dieser Aufruf ausgeführt werden.
Nächster Schritt beim Projektleiter: Vorbereitung samt Grenzen und Risiken
abnehmen und diese separate Forschungsentscheidung treffen. Keine weitere
Optimierung, keine Quellenbesichtigung und kein stiller Forschungsstart hier.

Unveränderte und neue vertragliche Grenzen vollständig:

- total_seconds: 57600
- worker_seconds: 54000
- completion_reserve: 3600
- job: 536870912
- preparation: 8388608
- source_total: 2097152
- source_case: 32768
- archives: 33554432
- gzip: 524288
- encoded: 4194304
- dictionary: 4194304
- record: 262144
- nodes: 65536
- edges: 262144
- indices: 65536
- collections: 16
- temp: 67108864
- export: 67108864
- administration: 2097152
- closure: 1048576
