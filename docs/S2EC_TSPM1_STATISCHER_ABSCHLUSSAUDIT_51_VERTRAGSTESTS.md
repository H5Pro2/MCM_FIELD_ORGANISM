# S2-EC: Statischer Abschlussaudit der 51 Vertragstests

## Auftrag und Quellstand

Gepruefter Repository-Stand:
`8ccfcf5c9f04f5ad4b5fd67299fda397543dc3c5`.
Quellstand der einmaligen S2-EB-Ausfuehrung:
`f4b16f33483d5751901da6f628467b59e8e4a385`.

Der Audit ist auf Quellen, Owner-Bindungen, Einmaligkeit, Ergebnisbelege,
Protokollzaehlung, T44/T48-T50, Codeunveraendertheit und Matrixsperre
begrenzt. Es wurden nur Dateien, JSON, Quelltext/AST und Git-Objekte
gelesen sowie gespeicherte Digests und Protokollzeilen nachgerechnet.
Keine Projektimporte, Testwiederholung, Zustandsfunktion oder
Vergleichszelle. S2-EC erhaelt keine Laufnummer.

## Belegkette

Die kanonischen Eigendigests von S2-DX, Prozessbeleg und abgeleiteter
Protokollauswertung stimmen. Die Einmalreservierung ist ueber ihren
Dateihash an den Prozessbeleg gebunden. Befehl, Quellcommit,
Freigabegrundlage und Startzeit stimmen in den zusammengehoerigen
Belegen ueberein; die Abschlusszeit liegt nach der Startzeit.

Gepruefte Hauptartefakte:

- `docs/S2DX_REPEAT_AFTER_S2EA_TSPM1_STATISCHER_IMPLEMENTIERUNGS_UND_TESTAUDIT_V1.json`
- `reports/s2eb_tspm1_51_contract_tests_attempt_v1.json`
- `reports/s2eb_tspm1_51_contract_tests_v1.json`
- `reports/s2eb_tspm1_51_contract_tests_transcript_verification_v1.json`

Die sieben protokollierten Quellendateien haben identische Hashes vor
und nach S2-EB sowie zum Auditzeitpunkt. Ihre Git-Blobs sind zwischen
Ausfuehrungscommit und Auditstand unveraendert. Die gesamte Git-Differenz
enthaelt nur die fuenf S2-EB-Dokumentations-/Ergebnisdateien; keine
Code-, Test-, API-, Snapshot- oder Feldpfadaenderung.

## Einmaligkeit und Zaehler

Der reservierte Versuch `s2eb.001` bindet genau einen Aufruf des
unittest-Moduls `tests.test_tspm1_s2dr_private_comparison_contract`.
Reservierung und Prozessbeleg nennen Versuch 1, keine Wiederholung.
Die nachfolgende Auswertung benennt ausdruecklich null neue Testaufrufe
und verwendet dasselbe unveraenderte Rohprotokoll.

Die 51 vollqualifizierten Testnamen im Protokoll stimmen einzeln mit dem
AST-Inventar der gebundenen Testklasse ueberein. T01-T51 erscheinen in
Reihenfolge, jeweils genau einmal und mit `ok`. Der Summarytext nennt
`Ran 51 tests in 1.351s`, der terminale Text lautet `OK`, der gespeicherte
Prozess-Exit-Code ist `0`. Keine Fehler, Fehlschlaege oder Skips.

Der urspruengliche Zaehler wird aus den gespeicherten Bytes nachvollzogen:
Die CRLF-Zeilenenden verhindern dessen Zeilenendmatch, weshalb er null
Einzelzeilen erkennt. Die separate Auswertung mit `splitlines` erkennt
die 51 vorhandenen Zeilen korrekt. Das ist eine korrigierte
Protokollauswertung, keine Wiederholung oder nachtraegliche Aenderung
eines Testresultats. Beide Belege bleiben unveraendert erhalten.

Massgebliche Rohbytes sind die UTF-8-Kodierung von `raw_output` im
Prozess-JSON. Deren SHA256 stimmt mit beiden Ergebnisbelegen ueberein.
Die Textansicht stimmt zeilenweise ebenfalls ueberein. Damit bleibt die
Pruefung unabhaengig von Git-Zeilenendennormalisierung der Textansicht.

Die Einmaligkeitsabnahme gilt fuer den dokumentierten autorisierten
S2-EB-Prozess und seine Belege; sie ist keine unabhaengige
Betriebssystemaufzeichnung saemtlicher Prozesse auf dem Rechner.

## Owner- und Negativtestabdeckung

`owner_for` bindet Zell-ID, Autorisierung, Plandigest, Konfiguration,
Fixture, Arm und Vorzustand an denselben Plan. `consume_once` prueft
Eigendigests, Autorisierungsformel und Owner-/Planrelationen vor dem
Zustandsaufruf. Die gebundenen Quellstellen und die ausgefuehrten
Assertions sind unveraendert.

| Test | Statisch zugeordneter, im Rohprotokoll mit ok bestaetigter Testinhalt |
| --- | --- |
| T44 | Kanonisch neu digestierter Plan mit fremder Autorisierung; innerer Fehler `S2DR_AUTHORIZATION_MISMATCH`, aeusserer Fehler `S2DR_ATTEMPT_FAILED`, Owner `FAILED`, kein freigegebener Ergebnisdigest. |
| T48 | Gueltige H1/B0-Vorbereitung und fremde H2/B0-Budgetquelle; Ablehnung mit `S2DR_RESULT_RELATION_MISMATCH`. |
| T49 | Ressourcengrenze 0, Verbrauch 1, Rest -1; relationale Ablehnung mit `S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED`. |
| T50 | H1/TSPM1 mit korrigierten Quellen-IDs; `formation_write_counts`, Index 1, Grenze 293, Verbrauch 294, Rest -1; derselbe relationale Budgetfehler. |

T44 prueft den Owner-Endzustand ausdruecklich ueber
`_assert_owner_failure`. T48-T50 pruefen den Ergebnisvalidator nach
einer gueltigen Owner-Vorbereitung; sie konsumieren den Owner nicht
erneut mit einem manipulierten Ergebnis. Der reparierte Helper
`rebuilt_result` bindet den neuen Budgetreceipt an Receipt und Ergebnis.

Die Owner-/Fehleraussagen sind durch die erfolgreichen Assertions und
ihre Quellbindung belegt. Es liegen keine gesonderten Laufzeit-Dumps
aller Owner, PPB-Aufrufzaehler oder Zwischenergebnisse vor; solche
zusaetzlichen Messungen werden nicht behauptet.

## Matrixgrenze und Entscheidung

Die Comparator-Pruefungen verwenden synthetische Ergebnisbelege.
Die im Testumfang enthaltenen Mikro-/Einzelzellenfixtures sind von
einer tatsaechlichen 7-mal-8-Vergleichsausfuehrung getrennt. Der
aufgezeichnete Testbefehl startet keinen Matrixrunner. Beide
Ergebnisbelege halten die Nichtausfuehrung der registrierten
56-Zellen-Matrix fest; diese bleibt weiterhin gesperrt.

`PASS_STATIC_S2EB_CONTRACT_TEST_CLOSURE`.

S2-EC nimmt den technischen Abschluss von S2-EB ab. Keine offenen
Blocker innerhalb dieses Auditumfangs. Keine neue Ausfuehrungsfreigabe.
Der Abschluss bestaetigt die vorhandenen Testaussagen, nicht jede
moegliche Mutation der R0-Projektion und nicht den Erfolg des spaeteren
funktionalen Vergleichs.

Es entsteht kein Memory-Nachweis und keine Bewertung der strukturellen
Qualitaet der Wahrnehmungsrepraesentationen. Diese Frage bleibt fuer den
nachfolgenden fairen Vergleich und die weitere Entwicklung offen.

Naechster vorgeschlagener Schritt: S2-ED als statischer
Ausfuehrungspreflight des bereits gebundenen 56-Zellen-Vergleichs am
aktuellen Quellstand, einschliesslich gleicher Budgets, Einmaligkeit,
Owner-/Receiptbindung und vollstaendiger Ergebnisaufzeichnung. Keine
neue Mechanik, keine Wiederholung der 51 Tests und noch keine Matrix-
oder Feldfreigabe.
