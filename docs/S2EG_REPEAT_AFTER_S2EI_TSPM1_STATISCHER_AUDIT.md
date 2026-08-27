# S2-EG: Statische Wiederholung nach S2-EI

## Entscheidung

**Statisch bestanden.**
`STATIC_IMPLEMENTATION_AND_TEST_AUDIT_PASSED_EXECUTION_LOCKED`.

Geprueft wurden die beiden in S2-EI belegten privaten Dateien gegen S2-EE
und S2-EH. Der Umfang bleibt eine Quellcode- und Vertragspruefung. Es wird
weder ein Testpass noch Laufzeitkorrektheit oder Produktionsdauerhaftigkeit
behauptet. Die 56-Zellen-Matrix bleibt gesperrt.

## Geschlossene Befunde

| Befund | Statische Abnahme |
| --- | --- |
| EG-B01 | `_validate_distance_source` akzeptiert ausschliesslich die gebundene S1-WU-Generatorstelle. Erfassung und spaetere Belegpruefung verwenden denselben Matcher. Am Erfassungsort werden Codeobjekt und Callee zusaetzlich gebunden. Keine pauschale Freigabe von Comprehensions. |
| EG-B02 | `_finish_publication` bindet Staging, SEALED, No-Replace, Final-Flush, Finalpruefung und terminales COMPLETED in dieser Reihenfolge. `_publication_failure` darf eine lesbare Datei ohne bestaetigten Final-Flush nicht als abgeschlossen einstufen. |
| EG-T01 | Genau neun bestehende Definitionen sind angepasst. Die 18 Quellen, fuenf Resultatfelder, 18 neutralen Beobachtungen, Methodikprioritaet, Rangfolge und vollstaendige R0-Projektion sind adressiert. T46 trennt Autorisierung und Duplikatpruefung. |

## Abschluss- und Fehlerpfade

Der positive Weg schreibt nach 112 Zelljournalzeilen `SEALED` als 113.
Erst nach erfolgreichem Final-Flush und Finalpruefung darf `COMPLETED` als
114 geschrieben werden. Reservierung, Ordinal, Vorgaenger, Artefaktdigest,
Status und Nullfelder der beiden Abschlusszeilen werden relational geprueft.
Alle vorangehenden Journalbelege werden ebenfalls gelesen und abgeglichen.

Der interne Final-Flush-Schalter ist anfangs falsch und besitzt genau eine
positive Setzstelle nach `store.publish()`. Die Publikationsfunktion selbst
enthaelt weiterhin den abschliessenden Volume-Flush. Ein dortiger Fehler
ueberspringt die positive Setzstelle. Ein lesbarer Finalbeleg kann diese
fehlende Bestaetigung im Fehlerzweig nicht ersetzen.

Scheitert der Flush der Terminalzeile, wird nur deren vollstaendige,
kanonische und gebundene Lesbarkeit zusammen mit dem vorher bestaetigten
Final-Flush und der Finalpruefung akzeptiert. Ein Teilbeleg scheitert.
Es gibt keinen zweiten Flush oder Publish-Aufruf im Fehlerzweig. Ein bereits
vollstaendig gepruefter Abschluss ist intern digestgebunden; spaetere Fehler
koennen keinen widerspruechlichen Fehlerabschluss anfuegen.

Die rein lesende `_verify_completion` verlangt Finalbeleg, Reservierung und
die vollstaendige Journalverkettung. Nach Prozessverlust reicht der
Artefaktstatus allein nicht. Dies setzt vertrauenswuerdig rekonstruierte
Pruefkontexte voraus; ein Recovery-Runner oder Resume-Pfad wurde nicht
eingefuehrt. Das Vorgehen bietet keinen Schutz gegen absichtlichen
Ledger-Rollback oder Belegfaelschung ausserhalb der bestehenden Vertrauensgrenze.

## Quellen und Tests

Compile-only der unveraenderten S1-WU-Datei findet genau ein Codeobjekt mit
`<genexpr>`, `probe_s1wu_perceptual_state.<locals>.<genexpr>` und Startzeile
209. Die zugelassene L1-Aufrufstelle liegt in 211-214. Der Matcher kompiliert
ohne Auswertung und ohne geerbte Compilerflags, mit der Optimierungsstufe
des laufenden Interpreters. Benannte Funktionen behalten ihre Quellpruefung.
Dimensionen, Belegfelder und Kostensummen bleiben unveraendert.

Die Comparator-Unterfaelle verwenden den echten `compare_s2dr_results`.
Nur die private Attestationspruefung wird waehrend des einzelnen
Unit-Aufrufs ersetzt und auf korrekte Argumente geprueft. Vorher und nachher
muss die echte Grenze die Testdaten verwerfen. Der Produktionscode enthaelt
keinen Testschalter. Die Generator- und Publikationsunterfaelle G1-G5/P1-P9
sind vorhanden. Kein Test wurde gesammelt oder ausgefuehrt.

TSPM-/PPB-Operatoren, `validate_s2dr_cell_result`, `_per_arm_metrics`,
`_rank_key`, `_decision_from_vectors`, `_exact_reduction_projection`,
`compare_s2dr_results` und die kanonischen Hashfunktionen sind AST-identisch
zum Ausgangsstand. Daher werden keine Erfolgsschwellen, Rangfolgen,
R0-Anforderungen oder Budgetinterpretationen neu eingefuehrt.

## Statische Belege

- Beide Dateien: AST und Compile-only erfolgreich; keine unaufgeloesten
  globalen Symbole in der statischen Symboltabellenpruefung.
- 51 Testdefinitionen; exakt T01, T34-T39, T46 und T51 geaendert.
- Elf literale Record-Konstruktorstellen feldgenau zum bestehenden Vertrag.
- Fuenf geschuetzte Quellhashes unveraendert. Die Testdatei ist durch die
  aktuelle Freigabe bewusst aus dem historischen Schutzumfang ausgenommen.
- Historische S2-EE-/EF-/EG-/EH-JSON-Digests stimmen weiterhin.
- `git diff --check` ohne Inhaltsfehler. Neue Rohbyte-/Blob-Belege separat.
- Keine Projektimporte, Registrybuilder, Zustandsfunktionen, Tests,
  Comparatoren, Veroeffentlichungsversuche oder Vergleichszellen ausgefuehrt.

## Naechste Grenze

RUECKMELDUNG ERFORDERLICH: Die einmalige Ausfuehrung der 51 angepassten
synthetischen Vertragstests benoetigt eine eigene ausdrueckliche Freigabe
mit vollstaendigem Ergebnisbeleg und Stopp bei Abweichung. Dieser Audit
erteilt keine Ausfuehrungsfreigabe. Die 56-Zellen-Matrix, oeffentliche API,
Snapshot und Feldintegration bleiben davon getrennt gesperrt.

WEITER: Am besten geht es jetzt mit der separat freizugebenden synthetischen
Vertragsvalidierung der 51 Definitionen weiter, nicht mit der Matrix.
