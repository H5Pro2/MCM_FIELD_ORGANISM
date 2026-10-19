# ZW1: gebundene Forschungsvorbereitung

2026-10-18 · Workflow f29d2dd0-a026-4045-acab-c4caebd7bdf8.
Status: Vorbereitung abgeschlossen und gebunden; keine Forschungsberechtigung.

## Ergebnis und Bindung

Das bestehende ZW1-Neutralpaket ist abgenommen und unverändert. Der neue tatsächliche
Supervisor-/Worker-Einstieg ist implementiert, mit fünf kurzen Integrationsszenarien
und elf fokussierten Prüfungen qualifiziert. Keine erneute Abnahme oder Wiederholung
der bisherigen 20 unveränderten Neutraltests. Deren Liefermanifest, Codeabhängigkeiten
und Matrix wurden stattdessen per Hash auf unveränderte Geltung geprüft.

Vorstart-SHA256: `28a1b008daaa9663a3f7ce3f403dc631526c0f7f78c2cebe82f8d89962e3dc13`.

Der vorhandene tatsächliche Validator experiments.zw1.prepare.validate_binding
bestätigt 2995 gebundene Dateien und 98 Qualifikationsartefakte.
Vollständiger Mengenabgleich für beide Gruppen erfolgreich. experiments/zw1 ist mit
allen vorhandenen Dateien erfasst, einschließlich Quellen, Statistik, Matrixrezept,
Tests, neutralem Paket und neuem Einstieg/Binder. Gemeinsame tools-, tests- und
mcm_field_organism-Pythondateien, AGENTS.md, Konzeptvertrag, relevante historische
Bindungen, Laufzeit-Executable/DLLs, sämtliche Grenzen, Quellenraum, Ziel,
Ausführungsplan und exakter Aufruf sind gebunden. Bytecodeerzeugung ist im zukünftigen
Aufruf und Worker durch -B deaktiviert.

Bootstrapmatrix unverändert:
`cd452bee76ea2b1b64c920afdd9c70211e5ba7abc7207049f4e7e280e5703f6c` (10000×16 Bytes).
Sie wurde kopiert und per SHA geprüft, nicht neu erzeugt oder nach Ergebnissen gewählt.

Exklusives Forschungsziel: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\zw1-comparison-16h-01`.
Reservierter Forschungsnamensraum: `MCM-ZW1/source/v1`.
Separate spätere Berechtigungsart: `ZW1_RESEARCH_ONCE`, exakt an obigen SHA gebunden.
Erwartetes Berechtigungsobjekt: kind, prestart_sha256 und allow_research=true;
zusätzliche/abweichende Felder, falscher Typ oder falsche Bindung werden abgewiesen.

**Exakter zukünftiger Aufruf, hier NICHT ausgeführt:**
Arbeitsverzeichnis `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.

```powershell
& 'C:\Python314\python.exe' '-B' '-m' 'experiments.zw1.prepare' 'run' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\zw1-research-preparation-20261018-01\prestart.json' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\zw1-research-preparation-20261018-01\authorization.json'
```

AUTHORIZATION/CONSUMED/ZIEL: authorization.json fehlt, CONSUMED.json fehlt,
Forschungsziel fehlt. Keine Forschungsquellen und keine 1024-Frame-Policyfälle erzeugt.
Der Binder erstellt ausschließlich Vorstartdateien. REPORT.md ist bewusst von der
Bindung ausgenommen, damit er den endgültigen SHA und Prüfstand nennen kann;
der gesamte ausführbare Stand und die Qualifikationsbelege sind gebunden.

## Tatsächlicher Einstieg und Paarabschluss

Neue getrennte Dateien: prepare.py, prepare_sources.py, prepare_series.py,
prepare_archive.py, test_prepare.py und bind_prepare.py unter experiments/zw1.
Die ursprünglichen E/F-/U-/Feedbackmodule sowie das abgenommene Neutralpaket bleiben
unverändert. Der neue Archivprüfer unterscheidet sich vom strukturell abgenommenen
ER1-Prüfer ausschließlich in der neuen Archivrevision ZW1_V1; fachliche Prüfungen
bleiben vollständig. Die Quellenmathematik und unabhängige Rekonstruktion wurden
neutral gegen die abgenommenen Funktionen abgeglichen; ergänzt wurde nur die
Zulassung des Forschungsnamensraums.

Vor Start prüft der Supervisor Bindung, Laufzeit, Grenzen und exakte separate
Einmalberechtigung. Verbrauchter Marker stoppt vor Zielanlage; ein vorhandenes Ziel
kann wegen exklusivem mkdir nicht wiederverwendet werden. Erst dann entstehen
CONSUMED.json und START.json. Kein Retry oder Resume nach Verbrauch oder Teilstart.
Der Supervisor startet genau einen Worker, bestätigt die Mitgliedschaft im gemeinsamen
harten 512-MiB-Job und öffnet erst danach das Worker-Gate. Quellenpermit erfordert
Bindung, Berechtigung, Start-/Verbrauchsmarker, korrektes Ziel und Jobmitgliedschaft.
Ohne diese Voraussetzungen bleiben Forschungsquellen und Policy-Ausführung gesperrt.

Alle 32 Bedingungsquellen werden vor dem ersten Forschungsarm generiert, unabhängig
rekonstruiert und versiegelt (16 Paarrekonstruktionen mit je zwei Bedingungsprüfungen).
Vor jeder Bedingung und Armerzeugung werden vollständiger Manifesthash, Quellenanzahl
und alle Quellenhashes erneut kontrolliert. Paar- und Bedingungsmetadaten bleiben
außerhalb der Policy. A/E, A/F, B/E und B/F sind frische Arme ohne Zustandsübertragung.

Eine Bedingung wird vollständig gemessen, archiviert, unabhängig geprüft und
bereinigt, bevor die nächste beginnt. Erst nach beiden Bedingungen, vier verschiedenen
Armobjekten und bestätigtem Arm-/Codec-Cleanup wird die Paarquittung geschrieben.
Zwischen Bedingungen bleiben nur kompakte Fehlerreihen und höchstens die vier
bereits geschlossenen Armobjekte des laufenden Paars. Nach Quittung werden auch
diese freigegeben; keine 64 Armobjekte oder parallelen A/B-Archive bleiben gehalten.

Fester Forschungsumfang: 16 Paare, 32 Geschichten, genau 64 Policy-Arme,
64 Live-Referenzen, 64 Archivrekonstruktionen, 32 Bedingungsquellenprüfungen,
eine unabhängige Statistikreferenz. Keine zusätzlichen Messarme. Einziger Primärkontrast
bleibt (E−F)A−(E−F)B mit allen 511 Zielen je Geschichte und vollständigen Paaren.
Die unveränderten Haupt-/Referenzstatistiken werden erst nach sämtlichen Paarquittungen
ausgeführt; Mittelwert, Paardifferenzen und Intervall müssen exakt übereinstimmen.

## Neue Integration: tatsächliche Ausführung

| Szenario | neue 96-Frame-Arme | bestandene Live-/Archivreferenzen | Quittierte Paare | Ergebnis |
|---|---:|---:|---|---|
| complete | 8 | 8 / 8 | 1,2 | TERMINAL_COMPLETE |
| source_failure | 0 | 0 / 0 | keine | SOURCE_CHANGED vor erstem Arm |
| archive_failure | 8 | 8 / 6 | nur 1 | PRIOR_RECORD_HASH in Paar 2/B |
| deadline | 4 | 4 / 4 | nur 1 | Supervisor-WORKER_DEADLINE |
| archive_budget | 8 | 8 / 6 | nur 1 | Archivfehler erhalten trotz Schreibbudgetfehler |
| Gesamt dieses Auftrags | 28 | 28 / 24 | fünf neutrale Paarquittungen | erwartete Zustände bestätigt |

Insgesamt 14 Bedingungs-Archivprüfaufrufe, davon zwölf vollständig bestanden und
zwei am absichtlich falschen Capture-Anker abgewiesen. Die beiden fehlerhaften
Archive sind keine erfolgreich rekonstruierten Armreferenzen. Das frühere
Neutralpaket hatte separat 16 kurze Arme; kumulativ bisher 44 neutrale Arme.
Keiner dieser Arme gehört zur noch ungestarteten Forschungsserie.

Alle fünf Szenarien bestätigen Workerende, Dateicleanup und leere geschlossene Arme.
Keine Partialdateien. Die Quellenfehlerprobe hat keinen Arm erzeugt.
Der Fristtest verwendet ausschließlich neutral 30 s statt 54000 s und wartet nach
dem ersten vollständig bereinigten Paar. Der Supervisor beendet den Worker tatsächlich
(Exitcode 1); Paar 2 bleibt offen. Dies belegt den Deadlinepfad, nicht ein nachträglich
bestätigtes In-Process-Cleanup eines mitten in einer Armoperation getöteten Workers.
Bei einem solchen realen Abbruch darf Cleanup UNCONFIRMED bleiben; kein Teilurteil.

Der Budgettest füllt die Administration gezielt auf 2097153 Bytes bei Grenze 2097152.
Der normale worker.json-Bericht fehlt erwartungsgemäß. Der reservierte 16-KiB-Terminalslot
bewahrt PRIOR_RECORD_HASH als erste Ursache und den Budgetfehler als Folgeursache.
Paar 1 bleibt quittiert, Paar 2 unquittiert; acht Arme waren bereits geschlossen.
Der abschließende Prozess-Exitcode allein wird nie als Forschungserfolg interpretiert.

Elf neue fokussierte Tests: neutraler Rezeptabgleich; Forschungsquellensperre;
exakter Berechtigungstyp einschließlich bool-Prüfung; vollständige Dateiabdeckung;
tatsächliche fünf Supervisor-/Worker-Abschlüsse; erste Ursachen und fehlende zweite
Paarquittung; unveränderte Statistik/kompakte Daten; fehlende Forschungsartefakte;
Zulassungsreihenfolge/Archivrevision; manipulierte Bindung/Dateiabdeckung/Aufrufe;
keine Zielanlage bei fehlender Berechtigung oder verbrauchtem Marker.
Alle 11/11 bestanden, dokumentiert in integration-tests.json und integration-tests.log.
Berechtigungsprüfungen verwenden ausschließlich In-Memory-Mocks, keine echte Berechtigung.

## Ressourcen und verbleibende Unsicherheit

Größter neutraler gemeinsamer Jobpeak: 66441216 Bytes (63,36 MiB).
Normalfall 23,56 s, Quellenfehler 0,85 s, Archivfehler 22,85 s, Fristprobe 30,02 s,
Budgetprobe 23,36 s. Vollständige Werte pro Szenario und alle Obergrenzen stehen
in resource-plan.json und RESOURCE_PLAN.md.

Kurzfall-Hochrechnung: 1993,69 s gesamte Fallarbeit für 32 Geschichten; vorsichtiger
Plan 16550 s plus 3600 s Abschlussreserve. Keine Vollgrößengarantie. Gerade lange
Erhaltungsketten sind in den kurzen Quellen nicht enthalten. ER1s realer Peak von
432316416 Bytes (412,29 MiB) bleibt maßgeblicher Warnpunkt: bis zur 512-MiB-Grenze
liegen nur 104554496 Bytes. Andere Wiederkehrmuster/Kompression können diesen
Abstand aufbrauchen. Serielles Freigeben und kompakte Fehlerdaten verringern
vermeidbare Haltung, beweisen aber keine Einhaltung bei 1024 Frames.

Grenzen unverändert gebunden: Worker 54000 s, gesamt 57600 s mit 3600 s Reserve;
gemeinsamer Job 512 MiB, höchstens Supervisor und ein Worker; Vorbereitung 8 MiB,
Quelle gesamt 2 MiB/je 32 KiB, Archive gesamt 32 MiB/je gzip 512 KiB,
encoded/dictionary je 4 MiB, Record 256 KiB, nodes/indices je 65536, edges 262144,
Collections 16, Temporär/Export je 64 MiB, Administration 2 MiB, Closure 1 MiB.
Policybudgets unverändert aus dem bestehenden E/F-Pfad. Kein Erhöhen aufgrund
identischer Armzahl. Der absichtliche Budgetfüllbestand ist Qualifikationsbeleg
innerhalb der Vorbereitung, keine erlaubte Überschreitung einer Forschungsserie.

## Erhaltung und abschließender Prüfnachweis

preservation.json dokumentiert unveränderte ursprüngliche ZW1-Lieferdateien und
Codeabhängigkeiten, ER1-v2-Code-/Qualifikationsbindungen und Forschungslieferung,
sowie die historischen v1-Datei-/Qualifikationsbindungen. Keine Neuauswertung alter
Archive, kein alter Forschungsstart. Die drei Übersichten erhalten einen neuen Stand.

Nach Fertigstellung erneut tatsächlichen Validator, vollständige Abdeckungsmengen,
Matrix-SHA und Abwesenheit von Berechtigung, Verbrauchsmarker und Ziel geprüft.
Finale Paketgröße einschließlich Bericht und Vorstartdateien: 3130501 Bytes
(Grenze 8388608). Keine offenen technischen Vorbereitungshindernisse; die ausdrücklich
benannte Vollgrößenunsicherheit bleibt bestehen.

Nächster Schritt: Projektleiter prüft das gebundene Paket und entscheidet gesondert
über einen einmaligen Forschungsstart. Aus dieser Vorbereitung folgt keine Berechtigung,
kein Retry, keine Umfangserweiterung und keine Änderung des ER1-Urteils INCONCLUSIVE.
