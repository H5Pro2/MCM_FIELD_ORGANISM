# ER1: gebundener Forschungseinstieg – Vorbereitung abgeschlossen

2026-10-17. Workflow `17468e31-58e4-46da-9b73-b3fff84058de`.
Status **VORBEREITET_UND_GEBUNDEN_OHNE_FORSCHUNGSFREIGABE**.

Der getrennte Einstieg ist implementiert, mit kurzen neutralen Fällen geprüft
und vollständig vorgebunden. Es wurde keine Forschungsberechtigung erstellt,
keine Forschungsquelle erzeugt, kein vollständiger 1024-Frame-Policyfall und
keine Forschungsserie ausgeführt. Das vorgesehene Forschungsziel existiert nicht.

## Exakte Bindung und zukünftiger Aufruf

[prestart.json](prestart.json), [prestart.sha256](prestart.sha256):

`8b00f9a27f958307e41673543ae294e8cffe9d2bf36949d2d71b3886b18b5bde`

Die Bindung umfasst 2967 Projektdateien: sämtliche Pythondateien
unter tools, mcm_field_organism und tests; die geltenden Projektregeln; den
ER1-Vertrag; die feste Bootstrapmatrix und die Prüfsummenliste des vorherigen
Neutralpakets. Zusätzlich sind 43 konkrete Vorbereitungsartefakte
gebunden. Interpreter, Python-DLLs und Laufzeitumgebung, sämtliche Vertragsgrenzen,
Quellennamensraum, Ziel, Ausführungszahlen und der exakte Aufruf sind festgeschrieben.
Die Bindung wurde nach dem Schreiben durch den tatsächlichen Validator gegengeprüft.
Die 51 Prüfsummen des vorigen Neutralpakets wurden unverändert bestätigt.

Arbeitsverzeichnis: `C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`.
Nur nach gesonderter Entscheidung und passend ausgestellter Einmalberechtigung:

```powershell
& 'C:\Python314\python.exe' '-m' 'tools.s2uc_er1_research_prepare' 'run' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\er1-research-preparation-20261017-01\prestart.json' 'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\er1-research-preparation-20261017-01\authorization.json'
```

Die Argumentliste steht zusätzlich unverändert in `prestart.json:call`.
Dieser Aufruf wurde nicht ausgeführt. Die erwartete spätere Berechtigung muss
exakt den Typ `ER1_RESEARCH_ONCE`, diesen Vorstart-SHA und `allow_research=true`
enthalten und am gebundenen authorization.json-Pfad liegen. Keine solche Datei
wurde erzeugt. Der Bericht oder die Vorstartbindung ersetzen keine Berechtigung.

## Zulassung und Verbrauch

`tools/s2uc_er1_research_prepare.py` prüft Pfad, Bindungshash, vollständige
Dateiabdeckung, jede Datei-/Qualifikationsprüfsumme, Laufzeit, Vertragsgrenzen,
Namensraum, Ziel, Aufruf und Ausführungsstruktur. Danach wird die separate
Berechtigung geprüft. Erst danach wird das Ziel exklusiv angelegt.

Der Start erzeugt exklusiv `CONSUMED.json` in der Vorbereitung und `START.json`
im Ziel. Bereits vorhandenes Ziel oder Verbrauchsmarker verhindern Wiederanlauf.
Die Einmalberechtigung wird nicht bei einem Fehler erneuert. Erst nach bestätigter
Windows-Jobzugehörigkeit erhält der Worker sein Gate. Der Worker prüft Bindung,
Berechtigung, Ziel, Verbrauchs- und Startmarker nochmals vor Quellenmaterialisierung.
Die Quellen-API verweigert Forschungsquellen ohne das dadurch erlangte Permit.
Die Forschungsfallfunktion prüft die Zulassung nochmals vor Armstart.

Fehler nach exklusiver Zielanlage lassen den Versuch geschlossen. Kein Retry,
Resume oder Ersatzlauf. Der alte neutrale Einstieg bleibt unverändert gesperrt
für Forschung; der neue Aufruf ist ausdrücklich ein anderer, separat gebundener Einstieg.

## Quellenbarriere und Ausführungsstruktur

Das festgelegte Rezept ist unverändert: 32 Geschichten, vier Cuefamilien,
getrennte SHA256-Cue-/Outcome-Ströme mit Rejection Sampling, 256 Viererblöcke,
48 Dimensionen, Wechsel nach Block 128 und feste Orientierungen. Die
Forschungsvariante benutzt ausschließlich `MCM-ER1/source/v1`; ihre Daten wurden
in dieser Vorbereitung nicht erzeugt. Der neutrale Rezeptpfad und seine
unabhängige Rekonstruktion wurden für alle 32 Kennungen gegen das vorhandene
qualifizierte Rezept verglichen, einschließlich sämtlicher Frames.

Im Forschungsworker werden alle 32 Quellen unabhängig rekonstruiert und geprüft,
mit Einzelhashes geschrieben und gemeinsam in sources-manifest.json versiegelt,
bevor der erste Arm angelegt werden darf. Der gemeinsame Manifest-SHA und die
Quellenbarriere stehen im reservierten Terminalzustand. Vor jedem Fall werden
Manifest und sämtliche Quellenhashes nochmals geprüft. Die positive neutrale
Integration benutzt dieselbe Quellenbarriere mit zwei expliziten kurzen Handfällen.

Exakt 64 Produktionsarme für 32 Geschichten. Jeder Arm wird **einmal** ausgeführt:
Einzeloperationsmessung, Vor-/Nachzustands-Capture und laufende unabhängige Referenz
begleiten denselben Durchgang. Keine zusätzlichen Mess- oder Capture-Policyarme.
Weitere 64 vollständige unabhängige Archivrekonstruktionen sind reine Referenzarbeit.
Die Statistik hat eine zusätzliche unabhängige Referenzauswertung, die Quellen
jeweils eine unabhängige Rekonstruktion. Alle diese Arbeiten stehen im
[Ressourcenplan](RESOURCE_PLAN.md). Es ist keine Vertragsausweitung auf mehr als
64 Policy-Ausführungen erforderlich.

## Vollständige Auswertung und Mechanismen

Das Serienaggregat verwendet E−F über alle 511 beobachtbaren Ziele jeder der
32 gleichgewichteten Geschichten, insgesamt 16352 Zielpaare. Keine Filterung nach
Abruf, Wärme oder günstigen Zielen. Die exakte rationale Auswertung, feste
16+16-stratifizierte Bootstrapmatrix und unabhängige Statistikreferenz bestätigen
Geschichtenmittel, Primärmittel, Intervall und getrennte Kostenbilanz.
Fehlende/ungeprüfte Fälle, zusätzliche Policy-Ausführungen oder Referenzfehler
verhindern ein vollständiges Nutzenurteil. Positive, negative und unentschiedene
synthetische Gesamtergebnisse sowie fehlende mechanistische Zeugen sind geprüft.

Das externe Mechanismenmodul trennt:

1. Erhaltene Originalspur über einen vollständigen ungleichen Zwischenblock und
   eine konkrete Konkurrenzpromotion; Gegenopfer und ursprüngliches Alter bleiben sichtbar.
2. Frühere tatsächlich akzeptierte lebende Rückmeldung desselben Offsets, vor
   der Konkurrenzpromotion und vor dem späteren Hinweis; keine Verwechslung mit
   dem Feedback des bewerteten Ziels oder einer wertgleichen Neuaufnahme.
3. Durchgehend erhaltene Originallinie und tatsächliche warme U-Auswahl.
4. Realisierter lokaler Fehlervergleich am identischen Ziel.

Vollständige Zeugen liegen in einer zusätzlichen begrenzten Archivsequenz und
werden bei der unabhängigen Archivreferenz erneut aus den bestätigten
Beobachterdaten rekonstruiert. Die starke globale Aussage wird nur bei einem
vollständigen lokalen E-Zeugen **und** negativem Primärintervall gesetzt.
Ereignisbezogene Nutzungszeugen können sich überlappen; sie werden nicht mit
Zielanzahlen addiert und ersetzen den vollen Primärnenner nicht.

Alle Blöcke, Bestätigungen, Aufnahmen, Ersetzungen, Opfer und späteren Folgeeffekte
bleiben im Archiv. Die Kostenseite ist nicht auf die erste Verdrängung begrenzt.
Gewinn, Schaden, maximaler Einzelschaden, schlechteste Geschichten und betroffene
Ziele bleiben separat. Warme Nutzung wird für E und F getrennt deskriptiv geführt.
U-Auswahl, Feedback, Kandidatenregeln und Policybudgets sind unverändert; CR1,
K1 und A1 sind deaktiviert. Beobachterinformationen erreichen die Policy nicht.

## Konkrete neutrale Integrationsnachweise

- [integration-complete/terminal.json](integration-complete/terminal.json):
  TERMINAL_COMPLETE, Fälle 1 und 2 quittiert, vier unterschiedliche Arme,
  vier begleitende Referenzen, vier Archivrekonstruktionen, keine Zusatzarme.
  44 und 32 Frames je Arm. Quellenbarriere bestätigt, Worker beendet,
  Arm- und Dateicleanup bestätigt, keine Partialdateien.
- [integration-complete/neutral-integrity.json](integration-complete/neutral-integrity.json):
  beide Archive PASS_DELTA_INTEGRITY. E nutzt Original 1–4 an Ziel 31 mit
  vorherigem Feedback an 7 und 19; F nutzt im Gegenfall Original 9–12 an Ziel 31
  mit Feedback an 15. Beide lokalen Kostenrichtungen bleiben belegt.
- [integration-admin/terminal.json](integration-admin/terminal.json):
  absichtlich 2097153 statt maximal 2097152 Administrationsbytes. Erwarteter
  TECHNICAL_ABORT; nur Fall 1 quittiert, Fall 2 nicht. Drei angelegte Arme
  geschlossen, Worker beendet, Dateicleanup bestätigt. Reservierter Terminalbericht
  überlebt das erschöpfte normale Schreibbudget.
- [integration-export/terminal.json](integration-export/terminal.json):
  absichtlich 67108865 statt maximal 67108864 Exportbytes einschließlich
  Vorbereitung. Erwarteter TECHNICAL_ABORT nach Fall 1; Fall 2 unquittiert,
  alle drei angelegten Arme geschlossen und Partialdateien entfernt. Auch der
  absichtlich unmögliche reguläre Workerbericht verdeckt die erste Ursache nicht.

Die Budgetüberschreitungen sind gezielte Fehlertests, keine tolerierten Grenzen
eines erfolgreichen Forschungsversuchs. Ein unkomprimierter neutraler
Administrationsfüllbestand bleibt als Beleg im Testverzeichnis erhalten und zählt
zum Vorbereitungsbudget. Vorherige kurze Integrationsstände vor der zusätzlichen
Manifestbarriere sind unter `../er1-research-development-01` unverändert erhalten.

[11/11 gezielte Tests](integration-tests.json), [Testprotokoll](integration-tests.log):

- `tests.test_s2uc_er1_research_entry.ER1Entry.test_01_research_sources_denied_without_permit`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_02_invalid_authorization_has_no_start_effect`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_03_exact_authorization_content`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_04_consuming_marker_exclusive_no_retry`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_05_neutral_recipe_matches_existing`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_06_case_receipt_only_after_success`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_07_full_statistics_and_mechanism_conjunction`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_08_incomplete_or_extra_policy_execution_no_verdict`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_09_real_integration_receipts_and_budget_closure`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_10_archive_tamper_and_source_reference_rejected`
- `tests.test_s2uc_er1_research_entry.ER1Entry.test_11_binding_scope_coverage_and_hashes`

Die Zulassungstests benutzen Berechtigungsinhalte nur als Mockdaten im Speicher.
Sie erzeugen keine Forschungsberechtigungsdatei. Der einmalige Verbrauch wird
mit isolierten neutralen temporären Ziel-/Markerpfaden und gemocktem Launcher
geprüft, ohne Quellenmaterialisierung oder Armstart. Reale Integrationsnachweise
benutzen dagegen den tatsächlichen Worker, Ledger, Archivpfad und Supervisor.

## Ressourcenplan und Grenzen

[RESOURCE_PLAN.md](RESOURCE_PLAN.md) und [resource-plan.json](resource-plan.json)
führen gemessene und hochgerechnete Werte getrennt auf. Lineare Planung über die
ungünstigeren kurzen Quotienten: bis 298624 gzip-Bytes je Geschichte und
9555968 Bytes für 32 Archive; Dictionary etwa 1.31 MB je Geschichte.
Beobachter, Mechanismen, Live- und Archivreferenzen sowie Statistik sind enthalten.
Planungsansatz: 13966 Sekunden Workerarbeit mit Unsicherheitsfaktor 8 und zusätzlichem
Puffer, danach 3600 Sekunden Abschlussreserve innerhalb der unveränderten Gesamtfrist.

Dies ist keine Vollgrößengarantie. Wachstum längerer Herkunftsketten, Kompression,
Peak-Allokationen und Dateiinventur können nicht aus kurzen Fällen garantiert werden.
Harte Grenzen bleiben 54000/57600 Sekunden, 512 MiB gemeinsamer Job, zwei Prozesse,
8 MiB Vorbereitung, sämtliche Einzel-/Gesamtdateigrenzen und Policyobergrenzen.
Jede Grenzverletzung führt zum technischen Abschluss ohne Teilserien-Nutzenurteil.
Kein vollständiger 1024-Frame-Policyfall wurde hierfür ausgeführt.

## Lieferung und nächste Entscheidung

Neu: die getrennten `tools/_s2uc_er1_run_*.py`-Integrationsmodule,
`tools/s2uc_er1_research_prepare.py`, `tools/s2uc_er1_research_qualify.py`,
`tools/s2uc_er1_bind.py` und `tests/test_s2uc_er1_research_entry.py`.
Die drei Projektübersichten sind auf den gebundenen Vorbereitungsstand aktualisiert.
Vorhandene fremde Änderungen und historisch gebundene Dateien wurden nicht verändert.
Keine Commits, kein Versandwerkzeug, keine Autorisierung und kein Forschungsstart.

Empfehlung: Projektleiter prüft genau dieses Vorstartpaket einschließlich
Ausführungszahlen und Vollgrößenunsicherheiten. Erst danach gesondert über eine
passende Einmalberechtigung für den oben gebundenen Aufruf entscheiden.
Keine erneute allgemeine Mechanismusprüfung oder zusätzliche Messarmserie vorschalten.
