# Neutraler V9-Herkunftsnachtrag: Wiederholung vom 29.09.2026

**79/79 PASS, keine Fehler oder Skips, Exit 0.** Der vollständige Anschlusscheck wurde auf ausdrücklichen Auftrag mit frischen neutralen Nichtnull-Fixtures und neuen Einmalidentitäten wiederholt. Kein Code wurde für die Wiederholung geändert. Der vorige Check war ebenfalls erfolgreich beendet worden; seine Ergebnisse bleiben erhalten.

Geprüft wurden erneut 70 bestehende betroffene Prüfpflichten und neun Anschlussprüfungen. Alle 175 bisherigen Prüfpflichten bleiben erhalten; die übrigen 105 wurden hier nicht erneut ausgeführt. Keine neue formale Gesamtqualifikation. Unittest-Zeit: 753,925 Sekunden; Runner einschließlich abschließendem Inventarabgleich: 773,224 Sekunden.

## Implementierung und Hashes

Das abgeschlossene Entwicklerpaket ergänzt ausschließlich die folgenden Dateien. Die bisherigen 59 Inventardateien bleiben unverändert. Die vollständige Codeunion umfasst **62 Dateien, 851840 / 851968 Byte; Rest 128 Byte**.

| Neue Datei | Byte | SHA-256 |
|---|---:|---|
| `tools/_s2uc_provenance_appendix.py` | 13955 | `f33e8bb35a1dcad2545d4b08562818763a3e2ddda5463732e523fb4fb2af38e7` |
| `tests/test_s2uc_provenance_appendix.py` | 10505 | `b08f6e9f22d6134f512b7427b75ad075e040fbde6dba1fb4c4da490ef3543aeb` |
| `tools/s2uc_appendix_check.py` | 3783 | `7d806abd63b66462fa0849ce778afc82c10acfa9b0d289fe06d385adf1998499` |

[Implementierungsbeschreibung und Aussagegrenzen](../provenance-appendix-development-20260920/REPORT.md). Der V9-Kindprozess behält sein 640-MiB-Job-Limit vor den Produktimports. Die anschließende Herkunftsauswertung und Nachtragspublikation laufen im Elternprozess; für ihn wird keine zusätzliche Prozessspeicherbegrenzung behauptet. Die Rechnung unten betrifft Artefaktbytes, keine RAM-Messung.

## Frischer Erfolgsabschluss

Produktidentität: `S2UC-V9-NEUTRAL-24d3c37e79294229b83f5e7d6de1e3bc`. Produktstatus **CLOSED_NEUTRAL_VERIFIED**, eigener Nachtragsstatus **PUBLISHED**. Der lesende Nachtragscheck besteht. Record, Verifikation und Terminal bleiben bytegleich mit den ursprünglichen Observer-Referenzen.

- [Produktterminal](cases/1/S2UC-V9-NEUTRAL-24d3c37e79294229b83f5e7d6de1e3bc/terminal.json)
- [Produktverifikation](cases/1/S2UC-V9-NEUTRAL-24d3c37e79294229b83f5e7d6de1e3bc/verification.json)
- [Produktrecord](cases/1/S2UC-V9-NEUTRAL-24d3c37e79294229b83f5e7d6de1e3bc/record.json)
- [Gespeicherter Herkunftsbericht](cases/1/appendix/provenance.json)
- [Nachtragsterminal und vollständige Dateibilanz](cases/1/appendix/appendix-terminal.json)
- [Prozesszulassung vor Imports](cases/1/observer/child-admission.json)
- [Alle Publikationsphasen und getrennte Statusfelder](cases/1/appendix-result.json)

## Gemeinsame Bytebilanz

| Konto | Byte | Unveränderte Grenze |
|---|---:|---:|
| Code | 851840 | 851968 |
| Metadaten | 28432 | 65536 |
| Static Shared einschließlich Observer-Kopien und Zusatzinventar | 180438 | 196608 |
| Record | 193150 | 245760 Reserve |
| Produktverifikation + Herkunftsbericht | **2466 + 75294 = 77760** | **131072 gemeinsam** |
| Beide Terminaldateien | 8590 | 16384 |
| Fehler / Minimal | 0 / 0 | je 16384 |
| Staging abschließend / Spitze | 0 / 75294 | 245760 |
| Shared gesamt | 189028 | 262144 |
| Gesamt / höchste Publikationskoexistenz | **1340210** | **4194304** |

Alle Grenzen eingehalten. Gemeinsame Verifikationsreserve: 53312 Byte frei. Metadaten, sämtliche Observer-Belege, Zusatzinventar und Staging sind vollständig gezählt. Temporäre Staging-Alternativen und Shared-Unterkonten werden nicht nochmals zum Abschluss addiert. [Maschinenlesbare Budgetrechnung](success-budget.json).

Operativer Rechnungsumfang: vollständiger Code, V9-Bundle, statisch gebundener Quellenplan, Produkt, Observer und Nachtrag. Die beiden ausführlichen Observer-Ergebniskopien zählen zusätzlich als Static Shared, übrige Observer-Steuerdaten als Metadaten, stderr als Fehlerbytes. Entwicklungsprotokolle außerhalb dieser Ablagen sind getrennte Audit-Artefakte und vollständig gehasht.

## Sieben Hintbefunde

| Hint | TW | UA | Vergleich |
|---|---|---|---|
| g1/12 | richtig | richtig | beide richtig |
| g1/24 | kein Match | richtig | Gewinn mit Erhaltungsnachweis |
| g1/26 | richtig | kein Match | Verlust |
| g2/38 | richtig | kein Match | Verlust vor Übernahme |
| g3/60 | richtig | richtig | beide richtig |
| g3/67 | richtig | kein Match | Verlust nach bestätigter Konkurrenz |
| g3/69 | richtig | richtig | beide richtig, kein Ausgleichsgewinn |

Getrennte Listen: Gewinne `[g1/24]`, Verluste `[g1/26, g2/38, g3/67]`. Keine Verrechnung. Die alte TW-Erwartung bei g1/24 bleibt verletzt und steuert die Herkunftsauswertung nicht. Alle konkreten Herkunfts-, Match- und Bestätigungsbelege stehen im gebundenen Herkunftsbericht. Diese synthetischen Befunde sind keine Ergebnisse realer NU-Quellen.

## Konkrete Anschlussprüfungen

Alle folgenden vollständigen IDs endeten mit PASS:

- `tests.test_s2uc_provenance_appendix.AppendixTests.test_bounded_process_to_seven_hint_report_with_full_budget`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_failed_appendix_rename_counts_staging_preserves_product`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_incomplete_product_never_calls_evaluator`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_input_changed_after_publication_is_rejected_by_reader`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_input_changed_during_publication_invalidates_appendix_only`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_invalid_product_terminal_never_calls_evaluator`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_joint_verification_reserve_plus_one_rejects_individually_small_report`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_observer_metadata_is_counted_and_overflow_blocks_evaluation`
- `tests.test_s2uc_provenance_appendix.AppendixTests.test_product_directory_cannot_be_used_as_appendix`

Die übrigen 70 erneut ausgeführten IDs und sämtliche Resultate stehen in [test-result.json](test-result.json); [unittest.log](unittest.log) enthält den tatsächlichen Durchlauf. Die neun Ablagen unter `cases/1` bis `cases/9` entsprechen alphabetisch den neun Anschlussprüfungen.

Abgewehrt werden unvollständige und ungültige Produktabschlüsse vor der Herkunftsauswertung, Änderungen während und nach Nachtragspublikation, ein injizierter Renamefehler, gemeinsam exakt 131073 Verifikationsbytes, eine Metadatenüberschreitung und die Verwendung des Produktverzeichnisses als Nachtrag. Produkt- und Nachtragsstatus bleiben getrennt. Bei bereits überschrittenem Eingabebudget kann die Fehlerpublikation selbst gesperrt sein; der äußere Prüfbeleg weist NOT_PUBLISHED und die gemessenen Istbytes aus, ohne einen gespeicherten Abschluss zu behaupten.

## Nachgeprüfte Erhaltung und Artefakthashes

223 vom Wiederholungsrunner erfasste Artefakte, 222 Artefakte des vorigen Checks, alle 62 Codehashes und alle 6117 vor dem Entwicklerpaket gebundenen Altdateien wurden anhand ihrer Originalbytes nachgeprüft. Alle Hashvergleiche stimmen. Keine historischen Records wurden neu ausgewertet. [Abschlusskontrolle](delivery-check.json).

| Artefakt | SHA-256 |
|---|---|
| `cases/1/S2UC-V9-NEUTRAL-24d3c37e79294229b83f5e7d6de1e3bc/record.json` | `32a3a8a9c05eb45721ad225ea4c574fb71b5d9dc2e3993f6d9c83b11b9426b29` |
| `cases/1/S2UC-V9-NEUTRAL-24d3c37e79294229b83f5e7d6de1e3bc/verification.json` | `e10113e0a5ac2ab1b442032770a318fd24fbd03a25a53ec25a205cb1d4a76bed` |
| `cases/1/S2UC-V9-NEUTRAL-24d3c37e79294229b83f5e7d6de1e3bc/terminal.json` | `0a91939ee1358984db848778a1ead11f2d4e1e80cda1513989a018297a729ec9` |
| `cases/1/appendix/provenance.json` | `1c628841898651bdd8525e322d45af1e9d79eaf48dbdb3bd49ae8590dcde8362` |
| `cases/1/appendix/appendix-terminal.json` | `23d2252e05eef33e017d607bc1731d9a4c2126a84530dd13e951d583b0479f30` |
| `dependency-inventory.json` | `faacf5b491421dc979757ded78cc4b0afd3bbb5e4779fc2945190c1ccc360229` |
| `test-result.json` | `3c29d399cbeb1d81323f916aed9ce130365b52ac15afd754d9ea08b1c948a27a` |

## Empfohlener nächster Schritt

Unabhängige Abnahme des neutralen Anschlusses anhand der getrennten Statusbelege, der sieben Hintbefunde und der gemeinsamen Bytebilanz. Diese Abnahme bleibt OPEN. Keine realen Quellen, keine Starteröffnung, keine Workflowänderung, kein Commit und kein Push.
