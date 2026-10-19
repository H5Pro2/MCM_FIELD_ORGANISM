# Getrennte herkunftsgebundene Auswertung – Entwicklerbericht

Version: `s2uc.provenance-outcomes.v1`. Auftrag: Implementierung des akzeptierten
[statischen Entwurfs](../gain-loss-static-design-20260920/ENTWURF.md), einschließlich
N1–N6, g1/24-Gegenprobe und Regression der bestehenden 161 Prüfpflichten.

**Abgeschlossen: 175/175 PASS – alle bisherigen 161 Prüfpflichten plus 14 neue
Prüfungen. Keine Fehler, keine Skips, Exit 0.** Die vollständige Codeunion liegt
mit 823597 Byte unter der unveränderten Grenze von 851968 Byte.

Abschlussbelege: [alle Test-IDs und Resultate](final/test-result.json),
[Rohprotokoll](final/unittest.log), [vollständiges Inventar](final/dependency-inventory.json),
[abschließender Gegencheck](delivery-check.json),
[Sieben-Zeitpunkte-Beispiel](final/fresh-evaluations/001/evaluation.json).

Die Implementierung ergänzt ausschließlich vier Dateien. Die alte Auswertung,
ihre Erwartungen, die sieben Zielbindungen, die Ausführungs- und Publikationspfade
und alle historischen Ergebnisse bleiben unverändert. Es wurden keine realen
NU-Quellen produziert und keine historischen Records mit der neuen Regel neu
bewertet. Die unabhängige Abnahme bleibt OPEN.

## Implementiertes Verhalten

`tools/_s2uc_provenance_evaluation.py` bietet `read_closed(binding_path, directory)`
als lesenden Zugang zu einem vollständig geschlossenen V9-Neutralabschluss.
Es gibt keinen Aufrufer im bisherigen Starter oder Publisher. Die neue Funktion
prüft aktuelle V9-Bindung, Verzeichnisidentität, genau Record/Verification/Terminal,
Bytegrenzen, JSON-Schlüssel, Artefakthashes, Abschlussstatus, Ausführungsbindung,
sechs geschlossene Owner und vollständige technische Recordkonsistenz.

Die Offlineprüfung prüft die gespeicherte Belegkette. Sie ist keine erneute
Quellenmaterialisierung und keine unabhängige Authentifizierung eines damaligen
Liveprozesses. Hashes binden konkrete Bytes; sie ersetzen keine externe
Vertrauenswurzel. Die Ergebnisdatei erteilt keine Ausführungsfreigabe.

Erst nach gültigem Gesamtabschluss werden die sieben unveränderten Zielbindungen
bewertet. Jede Generation ist durch Geschichte, Arm, Owner und Speicherrolle
qualifiziert. Gespeicherte Ursprungsformation und spätere Bestätiger bleiben
getrennt. Promotion übernimmt den älteren Kandidatenursprung; Wertgleichheit
einer Bestätigung erweitert keine Herkunftsmenge. Vollständige Matchlisten,
Offsets und Quellenpaare bestimmen den eindeutigen Zielabruf.

Ausgegeben werden die fünf Armklassen richtiger Zielabruf, anderer Abruf,
Mehrdeutigkeit, Enthaltung ohne Match und nicht bestimmbar. Ein fehlender Match
beweist keine Speicherleere; der aktuelle Bestand wird zusätzlich ausgewiesen.
Die alte `EXPECTED`-Erfüllung ist ein unabhängiges Vergleichsfeld.

Relative Zielabrufgewinne und -verluste stehen in getrennten Listen. Erhaltung
verlangt eine fortbestehende UA-Linie und die belegte Entfernung desselben alten
Zielursprungs bei TW. Ein Eindeutigkeitsgewinn bei weiter gespeicherter TW-Zielspur
ist keine bessere Speichererhaltung. Kandidatenersetzung vor Promotion,
Retained-Ersetzung durch bestätigte Konkurrenz und Verlust zuvor nachgewiesener
UA-Abrufbarkeit sind getrennte Zusatzbefunde; sie erhöhen die Gewinn-/Verlustzahl
nicht. Der letzte Befund bindet genau die vorher abgerufene, danach entfernte
UA-Linie. Es gibt keinen Saldo und keinen gemeinsamen Nutzenscore.

Ungültige oder unvollständige obligatorische Belege machen den Gesamtabschluss
`NOT_EVALUABLE`. Alle sieben Vergleiche und beide Gesamtzahlen bleiben dann
unbekannt (`null`), nicht null Gewinne bzw. null Verluste. Die leeren Falllisten
sind in diesem Fall ausdrücklich `NOT_DETERMINABLE` und nicht als Nullbefund
zu interpretieren.

Alle Herkunftsbezüge enthalten konkrete Pfade in den **dekodierten** Codec-Record
beziehungsweise ins Manifest. Frameattribute sind dabei adressierbar. Die
übergeordneten SHA-256-Werte beziehen sich stets auf die ursprünglichen
Eingabebytes; es werden keine Hashes eines umgeschriebenen Records unterschoben.

## Neue Dateien und vollständige Bytebilanz

| Datei | Byte | SHA-256 |
|---|---:|---|
| `tools/_s2uc_provenance_evaluation.py` | 26554 | `777f80beed3f8c26180c64ad8d91729f427345c30ce47bdf4a558d3e913d2cba` |
| `tools/_s2uc_provenance_inventory.py` | 1027 | `89228bcff7bd19886a626236611003a9c84840f258c915fee9ff18c52ebf7a15` |
| `tools/s2uc_provenance_check.py` | 5058 | `a830c7f42ad7ad79aab5edbc56d3f771355192e9c15ab10078e1f89f62af80fd` |
| `tests/test_s2uc_provenance_evaluation.py` | 15771 | `7480edcedd6d337f390708b4c13f9c59adde3fa6f0abf9b2ec95c3b7c0fac5f4` |

Vollständige Union: **59 Dateien, 823597 Byte**, unveränderte Grenze **851968 Byte**,
Rest **28371 Byte**. Darin sind sämtliche 55 bisherigen Dateien mit 775187 Byte
und alle vier Ergänzungen mit 48410 Byte enthalten, einschließlich neuer Tests
und neuem Nachweisrunner. Das Inventar erfasst die statische Importabhängigkeit
der vollständigen Einstiegsliste sowie die externe Python-/NumPy-/native
Laufzeitidentität. Externe Laufzeit und Ergebnisartefakte werden nicht als
Projektquellcode gezählt. Dies ist keine neue Prozessspeichermessung.

Der neue Inventarzugang ist separat. V9-Zulassung und frühere Budgetverträge
wurden nicht auf die neue Auswertung umgestellt. Kein Cap wurde erhöht.

## Neutrale Prüfungen

Fixtures werden ausschließlich innerhalb der neuen Tests frisch erzeugt.
Sie verwenden fünf neutrale synthetische PCM-Wellenformen und deren ausdrücklich
bezeichnete Kollisionsvarianten, 58 frische Materialisierungen pro Fixture und
die unveränderten Armübergänge. Die Fixture-Bindung trägt eine eigene Version
`s2uc.provenance-neutral-test-binding.v1`; sie ist keine gültige Starterbindung.
Ein zusätzlicher Test erstellt einen frischen V9-Neutralabschluss und prüft
den echten lesenden Zugang einschließlich Bytegleichheit aller Eingabedateien.
NU-Produktion ist dabei durch einen fehlschlagenden Mock gesperrt.

Fokussierter gebundener Check: **14/14 PASS, keine Fehler/Skips, Exit 0**.
Gesamtcheck: **175/175 PASS, keine Fehler/Skips, Exit 0**. Die unittest-Ausführung
dauerte 872,592 Sekunden; der dokumentierte Runnerabschnitt einschließlich
abschließendem Inventarabgleich 892,070 Sekunden. Die exakte ID-Menge stimmt;
Code und Laufzeitinventar sind vor/nach dem Lauf identisch. Alle 161 alten IDs
wurden zusätzlich mit dem bisherigen V9-Abschluss verglichen.

Der Gesamtcheck archiviert 29 ausschließlich frisch erzeugte Auswertungsfälle:
10 gültige neutrale Ergebnisse und 19 erwartete Nichtauswertbarkeiten. Alle
168 in [evidence-hashes.json](final/evidence-hashes.json) erfassten Artefakte
wurden anschließend erneut gegen Bytezahl und SHA-256 geprüft.

Die anfängliche direkte Entwicklungsprüfung hatte einen Fehler ausschließlich
in einer neuen Testassertion (Liste statt unverändertem Tupel der Zielbindung).
Die Assertion wurde korrigiert; der gebundene Check besteht. Fachliche
Erwartungen oder historische Daten wurden dafür nicht geändert.

Ausgeführte gebundene Befehle aus dem Projektverzeichnis:

```text
python tools/s2uc_provenance_check.py reports/s2uc/provenance-evaluation-development-20260920/focused-01 --focused
python tools/s2uc_provenance_check.py reports/s2uc/provenance-evaluation-development-20260920/final
```

Der Runner bindet die vollständige Union vor und nach dem Testlauf, verlangt
die exakte vorab aus den Testdateien ermittelte ID-Menge und lehnt Skips ab.
Jeder Aufruf der neuen Auswertung muss während einer neuen Provenienzprüfung
stattfinden; dabei werden die gerade erzeugten Eingabebytes und das Ergebnis
archiviert. Die alten 161 Prüfungen werden unverändert ausgeführt, ohne ihre
Records an die neue Herkunftsauswertung weiterzugeben.

Alle folgenden Methodennamen haben den vollständigen Präfix
`tests.test_s2uc_provenance_evaluation.ProvenanceTests.`.

| Fall | Testmethode | Geprüfter Befund |
|---|---|---|
| N1 | `test_n1_equal_values_do_not_change_stored_origin` | a=d und b=c: g1/26 meldet technischen Match aus A/p1, aber anderen Abruf statt B-Zielabruf; keine erfundene B-Kandidatenersetzung. |
| N2 | `test_n2_all_matches_kept_gain_is_not_preservation` | b=d: g3/60 TW mit zwei Matches, UA eindeutig; relativer Gewinn ohne Erhaltungsgewinn. |
| N2 Zusatz | `test_n2_multiple_offsets_same_generation_remain_ambiguous` | Drei Offsets derselben Generation bleiben drei Matches und mehrdeutig. |
| N3 | `test_n3_missing_origin_despite_success_is_unknown` | Erfolgstext bei fehlendem Materialisierungsbeleg wird nicht auswertbar, Zahlen bleiben unbekannt. |
| N4 Owner | `test_n4_owner_namespace_rejected_even_with_same_values_and_generation` | Falscher innerer Frame-Owner trotz gleicher Werte/Generation wird verworfen. |
| N4 Rolle | `test_n4_role_generation_namespace_not_interchangeable` | Kandidaten- und Retained-Generation dürfen nicht gleichgesetzt werden. |
| N5 | `test_n5_later_formation_cannot_repair_previous_hint` | Spätes g2-p3 repariert Hint 38 nicht; Kandidatenunterbrechung ist kein früherer Retained-Verlust. |
| N6 | `test_n6_competition_loss_and_new_target_not_netted` | A-Verlust bei 67 und beiderseitiger B-Abruf bei 69 bleiben getrennt, ohne Saldo/Doppelzählung. |
| g1/24 | `test_g1_24_distinct_values_expectation_conflict_independent` | TW ohne Match, alte Mehrdeutigkeitserwartung verletzt, UA-Abruf und Erhaltungsnachweis unabhängig. |
| Ursprung | `test_stored_and_confirming_origins_are_separate` | Älterer Kandidatenursprung bleibt erhalten; Bestätiger wird separat ausgewiesen. |
| Belegstellen | `test_record_manifest_hashes_and_every_pointer_resolve` | Originalbytehashes stimmen; sämtliche ausgegebenen Record-/Manifestpfade sind auflösbar. |
| Abschluss | `test_incomplete_failed_hash_and_real_scope_closures_unknown` | Fehlende Dateien, Fehlerterminal, falsche Hashes und Realquellenkennzeichnung bleiben unbekannt. |
| Manipulation | `test_invalid_receipt_and_incomplete_owner_not_rescued_by_rehash` | Neu versiegelte defekte Receipts, offener Owner, Teilrecord und boolesche Generation werden verworfen. |
| Lesender Zugang | `test_read_closed_fresh_v9_is_read_only_and_rejects_extra_error` | Frischer echter V9-Abschluss erfolgreich gelesen, Eingaben bytegleich; zusätzliche Fehlerdatei sperrt Auswertung. |

## Sieben-Zeitpunkte-Beispiel

Das Beispiel verwendet ausschließlich die frisch erzeugte **unterscheidbare
synthetische** Fixture. Es ist kein Befund zu realen NU-Werten und keine allgemeine
Überlegenheit der Kandidatenregel.

| Hint | Ziel | TW | UA | Vergleich |
|---|---|---|---|---|
| g1/12 | A | richtig | richtig | beide richtig |
| g1/24 | A | kein Match bei anderem Retained-Bestand | richtig | ein Zielabrufgewinn mit Erhaltungsnachweis |
| g1/26 | B | richtig | kein Match | ein relativer Verlust; einmaliger B-Kandidat vor Bestätigung ersetzt |
| g2/38 | A | richtig | kein Match, Retained leer | ein relativer Verlust; A-Kandidat durch Unterbrechung ersetzt |
| g3/60 | A | richtig | richtig | beide richtig |
| g3/67 | A | richtig | kein Match | ein relativer Verlust nach bestätigter B-Konkurrenz; früherer UA-Abruf bei 60 belegt |
| g3/69 | B | richtig | richtig | beide richtig; kein kompensierender UA-Gewinn |

Getrennte Listen: Gewinne `[g1/24]`, Verluste `[g1/26, g2/38, g3/67]`.
Abdeckung 7/7. g1/24 verletzt die unveränderte TW-Erwartung
`ABSTAIN_AMBIGUOUS_RETAINED_TRACE`; tatsächlich lautet die Entscheidung
`ABSTAIN_NO_RETAINED_TRACE`, mit leerer Matchliste. Dieses Erwartungsfeld steuert
die neue Herkunftsbewertung nicht.

Originalrecord des synthetischen Beispiels: 193055 Byte,
SHA-256 `831efc09ecb6d7828f8f97a14df587033f04f9ae4aba03b85f0634bf564a6078`.
Manifest: 24662 Byte,
SHA-256 `c1d7885ca46c7de996e0ee9b2bec3faf3c92c208f5aa94a007249fd5b6db4c6f`.
Der ausführliche maschinenlesbare Befund enthält alle Matchadressen,
Generations-/Ownerbezüge, Ursprungs- und Bestätigungsereignisse sowie Mechanismen.

## Hashbindungen der Abschlussartefakte

| Artefakt | Byte | SHA-256 |
|---|---:|---|
| `final/test-result.json` | 45341 | `f4dd47f5d450ac081c76ebe38be7de51b1d4277122884f40a3f49355abc954f3` |
| `final/dependency-inventory.json` | 12601 | `e5ba7ed81d355d3f1113ef8b64754938c2d9552ff7bff26b8fa0111a1f3449c7` |
| `final/evidence-hashes.json` | 23173 | `a5214fd5b6c08e9018d7a63c6e5e540d15755e7eba8393098249ff08571d5262` |
| `final/fresh-evaluations/001/evaluation.json` | 74968 | `b3d1eb1ab427a21509d2a996b9177af1cb732234681f6ea5c1383daa76f7de0c` |

Die vollständigen neuen Test-IDs stehen oben und maschinenlesbar im Testresultat;
die übrigen 161 vollständigen IDs sind dort ebenfalls jeweils mit PASS enthalten.
Das [Captureverzeichnis](final/captures.json) ordnet jede archivierte Fixture
dem tatsächlich ausgeführten Test zu. Das Beispiel stammt aus der g1/24-Gegenprobe.

## Erhaltung und Aussagegrenzen

[before.json](before.json) und [preservation-check.json](preservation-check.json)
belegen nach dem vollständigen Regressionslauf 5769 unveränderte Altdateien mit
zusammen 68981109 Byte. Dafür wurden
ausschließlich ursprüngliche Dateibytes und SHA-256 verglichen; historische
Records wurden nicht fachlich neu ausgewertet. Alle 55 bisherigen Inventardateien
sind in der neuen Union identisch enthalten. Der Repo-Stand enthält bereits
fremde Änderungen; diese wurden nicht verworfen oder in einen Commit übernommen.

Der ergänzende [Baseline-/Unionsabgleich](baseline-union-check.json) bindet die
unveränderten 161 IDs und 55 Dateien an das neue vollständige Inventar.

Die bestehende technische Regression ist Teil dieses Entwicklerpakets, keine
erneuerte formale Qualifikation. Auch nach erfolgreicher Regression bleiben
unabhängige Abnahme, Realeinstieg und reale Quellenproduktion unverändert offen
beziehungsweise gesperrt. Keine Workflowänderung, kein Commit, kein Push.

## Empfohlener nächster Schritt

Der Projektleiter sollte die getrennte Auswertung anhand der archivierten
Gegenproben und Belegpfade unabhängig abnehmen. Besonders zu prüfen sind die
Trennung von Herkunft und Wertgleichheit, die Mechanismusbelege sowie das
unverändert separat ausgewiesene g1/24-Erwartungsproblem. Eine spätere Anbindung
an einen Ausführungspfad benötigt einen eigenen Auftrag; dieses Paket öffnet
keinen realen Lauf.
