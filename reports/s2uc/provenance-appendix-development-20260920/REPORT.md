# Neutraler V9-Prozess mit getrenntem Herkunftsnachtrag

Auftrag: frischen synthetischen Nichtnull-Lauf über den begrenzten V9-Einstieg
abschließen und erst nach gültigem Produktabschluss einen getrennt gebundenen
Herkunftsbericht publizieren. Gemeinsame Verifikationsreserve 131072 Byte,
Codegrenze 851968 Byte; beide unverändert.

**Abgeschlossen: 79/79 Prüfungen bestanden, keine Fehler oder Skips, Exit 0.**
Der Prozess beendete den Check auch während der Kommunikationsunterbrechung.
Bei Wiederaufnahme am 29.09.2026 wurden die 222 archivierten Artefakte und die
62 Codehashes nachgeprüft. Die ausdrücklich angeforderte Wiederholung erhält
eine eigene Ablage unter `../provenance-appendix-repeat-20260929-01`.

Nachweise: [Test-IDs und Resultate](final/test-result.json),
[Rohprotokoll](final/unittest.log), [vollständiges Inventar](final/dependency-inventory.json)
und [Artefakthashes](final/evidence-hashes.json).
Die unittest-Ausführung dauerte 804,104 Sekunden; der dokumentierte Runnerabschnitt
einschließlich abschließendem Inventarabgleich 822,852 Sekunden.

## Änderung und Statusmodell

Neu sind ausschließlich `tools/_s2uc_provenance_appendix.py`,
`tests/test_s2uc_provenance_appendix.py` und `tools/s2uc_appendix_check.py`.
Alle bisherigen 59 Inventardateien einschließlich des Herkunftsevaluators und
sämtlicher 175 Prüfpflichten bleiben unverändert.

| Neue Datei | Byte | SHA-256 |
|---|---:|---|
| `tools/_s2uc_provenance_appendix.py` | 13955 | `f33e8bb35a1dcad2545d4b08562818763a3e2ddda5463732e523fb4fb2af38e7` |
| `tests/test_s2uc_provenance_appendix.py` | 10505 | `b08f6e9f22d6134f512b7427b75ad075e040fbde6dba1fb4c4da490ef3543aeb` |
| `tools/s2uc_appendix_check.py` | 3783 | `7d806abd63b66462fa0849ce778afc82c10acfa9b0d289fe06d385adf1998499` |

Vollständige Union: **62 Dateien, 851840 Byte**, unveränderte Codegrenze
**851968 Byte**, Rest **128 Byte**. Der [Baselineabgleich](baseline-union-check.json)
bindet die erhaltenen 175 Test-IDs und 59 alten Dateien an die drei Ergänzungen.

Der explizit neutrale Aufruf `run_neutral(binding_path, observer=…, directory=…)`
führt zuerst den vorhandenen V9-Prozesseinstieg aus. Der Kindprozess bleibt unter
der bestehenden Windows-Job-Grenze von 671088640 Byte (640 MiB), mit Zulassung
vor Produkt-/NumPy-Imports. Die Herkunftsauswertung und Nachtragspublikation
laufen anschließend lesend beziehungsweise schreibend im aufrufenden Elternprozess.
Für diesen wird keine zusätzliche Prozessspeicherbegrenzung behauptet. Die
Nachtragsrechnung betrifft die vollständigen zugeordneten Artefaktbytes.

Vor der Auswertung werden Prozessabschluss, Observerbindung, Limitbelege,
58 Quellenaufrufe ohne reale Quellenproduktion und die ursprünglichen Produkt-
Bytebezüge geprüft. Anschließend prüft der vorhandene lesende Evaluator den
vollständigen Produktabschluss. Ein ungültiger Prozess-/Produktbeleg führt
vorher zur Ablehnung. Der reale Starter erhält keinen neuen Aufrufpfad.

Die frische Nachtragsablage enthält im Erfolgsfall genau:

- `dependency-inventory.json`: vollständige neue Codeunion samt Laufzeitidentität;
- `provenance.json`: unveränderte Herkunftsbewertung mit sieben Hintbefunden,
  Auswertungsversion, Hash des Inventars und Hash der gesamten Eingabereferenzliste;
- `appendix-terminal.json`: eigener Publikationsstatus, Bindungen, vollständige
  Artefaktzuordnung und selbstgrößenstabile Bytebilanz.

Record, Produktverifikation und Produktterminal werden nicht beschrieben.
Quellbundle, Produkt, Observer und Nachtrag müssen disjunkte Verzeichnisbäume
sein; ein bestehender Nachtrag wird nicht überschrieben. Eine einzelne feste
Staging-Datei wird exklusiv geschrieben, bytegleich nachgelesen und auf demselben
Dateisystem umbenannt. Es wird keine Stromausfall- oder Crash-Recovery zugesagt.

Der eigene Status `PUBLISHED` beziehungsweise `NOT_PUBLISHED` steht neben
`product_status_reported`, `product_validated_before_appendix` und
`product_inputs_unchanged`. Ein ursprüngliches `CLOSED_NEUTRAL_VERIFIED` ist
bei später beschädigten Bytes nur der unveränderte gemeldete Produktstatus,
kein erneuter Integritätsnachweis. Ein Publikationsfehler kann einen zuvor
gültigen Produktabschluss nicht umschreiben. Nachtragsergebnisse sind nur mit
gültigem eigenen Abschluss nutzbar; einzelne vorhandene Berichtsdateien genügen
nicht. Ein Fehlerbeleg wird nach Möglichkeit getrennt veröffentlicht.

`read_appendix` prüft vor späterem Konsum alle gebundenen Eingabe- und
Nachtragsbytes, das aktuelle Inventar, die Auswertungsversion, die Prozessbelege
und die vollständige Bytebilanz erneut. Es führt keine neue Herkunftsauswertung
durch. Bei Änderungen lautet sein Status `INVALID`, auch wenn ein altes
Nachtragsterminal weiterhin `PUBLISHED` enthält. Hashbindungen sind
Integritätsbezüge, keine externe Authentifizierung eines Liveprozesses.

## Vollständiger Rechnungsumfang

Jede Rechnung umfasst die vollständige Codeunion, alle V9-Bundle-Dateien,
den bereits gebundenen NU-Plan als bloße statische Referenz, alle vorhandenen
Produktdateien, sämtliche Observer-Dateien und sämtliche Nachtragsdateien.
Unregistrierte Dateien und Pfad-/Dateialiase werden nicht als unsichtbare
Restmenge akzeptiert. Code wird über das mitgeführte vollständige Inventar
einmal gezählt; jeder ursprüngliche Codehash wird bei den Snapshots geprüft.

Die beiden ausführlichen Observer-Kopien `result.json` und `process-exit.json`
sind zusätzlich gezählte statische Prozessbelege (`static_shared`). Observer-
Konfiguration, Zulassungsbelege und übrige Steuerdaten zählen als Metadaten;
`stderr.txt` zählt als Fehlerbytes. Keine dieser Kopien wird aus dem Gesamtumfang
herausgerechnet. Das zusätzliche Inventar zählt ebenfalls als `static_shared`.

Die ursprüngliche `verification.json` und die vollständige neue
`provenance.json` belasten gemeinsam das Verifikationskonto und dessen
unveränderte Reserve von 131072 Byte. Beide Terminaldateien belasten gemeinsam
das Terminalkonto. Jede Publikation prüft vor dem Schreiben sowohl die
Staging-Koexistenz als auch den Zustand nach Umbenennung. Staging wird tatsächlich
nachgelesen; beim injizierten Fehler werden seine verbliebenen Bytes vor der
Bereinigung gesondert beobachtet. Die eigenen Terminalbytes gehen über eine
Fixpunktrechnung vollständig in die Abschlussbilanz ein; ihr eigener Hash wird
außerhalb dieser Datei gebunden, um einen zirkulären Eigenhash zu vermeiden.

Die äußeren unittest-Protokolle, Testresultate und Berichtskopien sind separate
Entwicklungsnachweise. Sie gehören nicht zur operativen Vier-Verzeichnis-Rechnung
Bundle/Produkt/Observer/Nachtrag, werden aber im Entwicklungsarchiv vollständig
gehasht. Es gibt keine Behauptung einer Prozess-RAM-Messung aus Quellbytezahlen.

## Gespeicherter neutraler Erfolgsbeleg und Bytebilanz

Frische Produktidentität: `S2UC-V9-NEUTRAL-1722e07838514d44b314909fd7fe1d32`.
Produktstatus `CLOSED_NEUTRAL_VERIFIED`, eigener Nachtragsstatus `PUBLISHED`;
der anschließende lesende Konsum bestätigt `VERIFIED`. Die ursprünglichen
Record-/Verifikations-/Terminalbytes stimmen mit den vor dem Nachtrag erhobenen
Bytes und den Observer-Referenzen überein.

Belegpfade:

- [Produktterminal](final/cases/1/S2UC-V9-NEUTRAL-1722e07838514d44b314909fd7fe1d32/terminal.json)
- [Produktverifikation](final/cases/1/S2UC-V9-NEUTRAL-1722e07838514d44b314909fd7fe1d32/verification.json)
- [Produktrecord](final/cases/1/S2UC-V9-NEUTRAL-1722e07838514d44b314909fd7fe1d32/record.json)
- [Herkunftsbericht mit sieben Hintbefunden](final/cases/1/appendix/provenance.json)
- [Nachtragsterminal mit vollständiger Artefaktbilanz](final/cases/1/appendix/appendix-terminal.json)
- [Alle Publikationsphasen und Statusfelder](final/cases/1/appendix-result.json)
- [Gemeinsamer Budgetnachweis](success-budget.json)
- [Zulassung im begrenzten Kindprozess](final/cases/1/observer/child-admission.json)

| Konto | Gemessene Abschlussbytes | Unveränderte Grenze |
|---|---:|---:|
| Vollständiger Code | 851840 | 851968 |
| Metadaten | 28466 | 65536 |
| Static Shared einschließlich Observer-Ergebniskopien und Zusatzinventar | 180618 | 196608 |
| Record | 193150 | 245760 Reserve |
| Produktverifikation + Herkunftsbericht | **2466 + 75294 = 77760** | **131072 gemeinsame Reserve** |
| Produkt- und Nachtragsterminal zusammen | 8590 | 16384 |
| Fehler / Minimal | 0 / 0 | je 16384 |
| Staging nach Abschluss | 0 | 245760 |
| Höchste Staging-Koexistenz | 75294 | 245760 |
| Shared gesamt (Unterkonten nur einmal gezählt) | 189208 | 262144 |
| Gesamt / höchste Publikations-Koexistenz | **1340424** | **4194304** |

Die gemeinsame Verifikationsreserve hat 53312 Byte Rest. Die Staging-Zeile ist
eine temporäre Alternative zur fertigen Datei, kein zusätzlich zum Abschluss
nochmals addierter Dauerbestand. Alle sechs Vorabkonten der drei atomaren
Publikationen halten die Grenzen ein; die Bytegleichheit des jeweiligen Stagings
wird vor der Umbenennung geprüft.

| Artefakt | Byte | SHA-256 |
|---|---:|---|
| Produkt `record.json` | 193150 | `9cae960b7283a17c523093d649364065646f2057e62d4af837912bbc2bf15271` |
| Produkt `verification.json` | 2466 | `a82f2173426776507b9fcabdcc564dc17d13281b99aae8bf7be21d6c0a2e82da` |
| Produkt `terminal.json` | 1644 | `53500e681f1c662d4483d00732f61d82e2ea97fd89a3b7b004d5e270b1b495cb` |
| Nachtrag `provenance.json` | 75294 | `0ef1445bddd4af45afdf4283f5cdf5594bf784a004c0be27f52b097ffc111fd2` |
| `appendix-terminal.json` | 6946 | `b223b78423fdc730a5d826732ccd66e15c944e6d123888c7a5dd3438001f97ce` |

| Hint | TW | UA | Separater Vergleich |
|---|---|---|---|
| g1/12 | richtiger A-Abruf | richtiger A-Abruf | beide richtig |
| g1/24 | kein Match | richtiger A-Abruf | ein Gewinn mit Erhaltungsnachweis |
| g1/26 | richtiger B-Abruf | kein Match | ein Verlust |
| g2/38 | richtiger A-Abruf | kein Match | ein Verlust vor Übernahme |
| g3/60 | richtiger A-Abruf | richtiger A-Abruf | beide richtig |
| g3/67 | richtiger A-Abruf | kein Match | ein Verlust nach bestätigter Konkurrenz |
| g3/69 | richtiger B-Abruf | richtiger B-Abruf | beide richtig, kein Ausgleichsgewinn |

Die alte TW-Erwartung bei g1/24 bleibt verletzt und separat ausgewiesen. Der
neutrale Befund ist kein Ergebnis für reale NU-Quellen und keine allgemeine
Überlegenheitsaussage. Vollständige Herkunfts-, Match- und Bestätigungsbelege
stehen im gebundenen Bericht; es wurde keine historische Liste neu befüllt.

## Gegenproben und Regression

Alle neuen Fixtures und Produktläufe entstehen frisch in dieser Testsuite.
Die neuen Tests sperren beziehungsweise beobachten die vorhandene rein neutrale
Quellenroute des begrenzten V9-Prozesses. Bestehende historische Records werden
nicht an den Evaluator übergeben. Die archivierten V9-Testbelege wurden bei der
Vorbereitung nur strukturell gelesen, nicht neu ausgewertet.

Der erste fokussierte Check bestand acht Prüfungen; die gemeinsame Budgetprobe
endete vor ihrem eigentlichen Prüfziel mit einem Fehler. Ihr langer Ablagepfad
verhinderte unter Windows bereits die ursprüngliche Produktpublikation. Dieser
neutrale Fehlversuch bleibt unter `focused-01` erhalten. Die Testablage verwendet
nun kurze nummerierte Fallverzeichnisse, bei unveränderten vollständigen IDs im
Protokoll. Die Testhilfe fordert außerdem ausdrücklich den erwarteten Produktstatus.
Weder der Produktcode noch ein Budget wurde zur Behebung verändert.
Die korrigierte einzelne Budgetgegenprobe bestand anschließend (1/1, Exit 0);
der finale gemeinsame Check bindet alle neuen Fälle erneut an das endgültige Inventar.

Vollständiger Präfix aller neuen Test-IDs:
`tests.test_s2uc_provenance_appendix.AppendixTests.`

| Testmethode | Abnahmekriterium |
|---|---|
| `test_bounded_process_to_seven_hint_report_with_full_budget` | Vollständiger begrenzter Prozess bis zum gespeicherten und nachgelesenen Sieben-Hint-Bericht; alle Dateien gezählt, Produkt bytegleich. |
| `test_incomplete_product_never_calls_evaluator` | Speicherfehler bei Aufruf 58, unvollständiges Produkt: keine Herkunftsauswertung. |
| `test_invalid_product_terminal_never_calls_evaluator` | Nachträglich ungültiger Produktabschluss: keine Herkunftsauswertung. |
| `test_input_changed_during_publication_invalidates_appendix_only` | Änderung nach Berichtsumbenennung sperrt den Nachtragsabschluss; Produktterminal bleibt unverändert. |
| `test_input_changed_after_publication_is_rejected_by_reader` | Spätere Eingabeänderung wird beim Konsum zurückgewiesen. |
| `test_failed_appendix_rename_counts_staging_preserves_product` | Gescheiterte Nachtragspublikation zählt Rest-Staging, meldet eigenen Fehler und erhält Produktbytes. |
| `test_joint_verification_reserve_plus_one_rejects_individually_small_report` | Ein Bericht unter 131072 Byte wird verworfen, wenn er gemeinsam mit der Verifikation genau 131073 Byte belegt. |
| `test_observer_metadata_is_counted_and_overflow_blocks_evaluation` | Observer-Metadatenüberschreitung verhindert die Auswertung; vollständige Istbytes bleiben sichtbar. |
| `test_product_directory_cannot_be_used_as_appendix` | Nachtrag kann nicht in das Produktverzeichnis schreiben. |

Die betroffenen bestehenden Suiten sind Herkunftsauswertung (14),
V9-Quellenausführung (17), Ressourcenvertrag (14), V9-Prozessschutz (6) und
Publikation (19), zusammen 70 Prüfpflichten. Mit neun neuen Prüfungen umfasst der
gemeinsame Anschlusscheck 79 Tests. Die übrigen 105 vorhandenen Prüfpflichten werden in diesem Auftrag
nicht nochmals ausgeführt; ihre Dateien und der bisherige Nachweis bleiben
unverändert erhalten. Das ist keine neue formale Gesamtqualifikation.

Die finalen Fallablagen entsprechen der alphabetischen Testreihenfolge:
1 Erfolg, 2 Renamefehler, 3 unvollständiges Produkt, 4 Änderung nach Publikation,
5 Änderung während Publikation, 6 ungültiges Produktterminal, 7 gemeinsames
Verifikationsbudget plus ein Byte, 8 Metadatenüberschreitung, 9 Verzeichnisabwehr.
Jeder ausgeführte Produktprozess hat sein eigenes frisches Bundle und seine
eigene Einmalidentität. Bei bereits überschrittenem Eingabebudget kann auch
die Fehlerpublikation gesperrt bleiben; der äußere Prüfbeleg weist dann die
gemessenen Überschreitungen und `NOT_PUBLISHED` aus, ohne einen gespeicherten
Nachtragsabschluss zu behaupten.

## Nächster fachlicher Schritt

Empfohlen ist die unabhängige Abnahme des neutralen End-to-End-Anschlusses anhand
des Produktabschlusses, der sieben Herkunftsbefunde, der Fehlerfälle und der
gemeinsamen Ressourcenrechnung. Die unabhängige Abnahme bleibt OPEN. Eine reale
Quellenproduktion oder Öffnung des Starters folgt daraus nicht. Keine Änderung
am Workflow, kein Commit und kein Push.
