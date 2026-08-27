# S2-EA: Quellen-ID-Korrektur und statischer S2-DX-Abschluss

## Auftrag und Quellstand

Korrekturcommit: `10823cce4c2cd78133bf51c0117662a5d79d240e`.
Vorgaenger: `f252e226d3aadb25cec25406ef69125e5a226256`.
Vorgaengeraudit: S2-DX nach S2-DZ, Artefaktdigest
`ceaafe7998a7350749f5b182890b8f131a5ce2c457cee91a24660f876fd78f4c`.

Die ausdrueckliche S2-EA-Freigabe erlaubt ausschliesslich die Korrektur
der privaten Quellen-ID-Erzeugung und anschliessend einen statischen Audit.
Keine Projektmodule, Zustandsfunktionen, Tests, Comparatoren oder
Vergleichszellen wurden ausgefuehrt. Es wird keine Laufnummer vergeben.

## Korrektur

Nur `mcm_field_organism/_tspm1_s2dr_private_comparison.py` wurde geaendert.
Vier Formatierungen verwenden jetzt `history_id.lower()`:

- registrierte Bildungs-Frame-ID, Zeile 565;
- registrierte Probe-Frame-ID, Zeile 566;
- tatsaechliche Rezeptor-Frame-ID, Zeile 932;
- Envelope-Bindungs-ID, Zeile 950.

Die fachliche Geschichtsrolle bleibt `H1`, einschliesslich Registry,
Zellplan, Finding und T50-Aufruf. Nur der daraus abgeleitete technische
Namensanteil lautet `h1`. Beispiele aus der statischen Formatierung:
`s2dr.h1.formation.001.auditory` und
`s2dr.binding.h1.formation.001`.

Die gemeinsame private Formatierung gilt konsistent auch fuer die anderen
bereits registrierten H1-H7-Rollen. Ihre Zuordnung bleibt eindeutig; keine
Geschichte wird zusammengelegt, ersetzt oder inhaltlich geaendert.
Modalitaeten, Werte, Quellenzeiten, Eingabe- und Speicherbudgets bleiben
unveraendert. Der Rezeptorvertrag wird nicht gelockert.

## Statischer Wiederholungsaudit

### DX-ZB01 ist geschlossen

Die technische Frame-ID und die Envelope-ID entsprechen jetzt dem
unveraenderten Muster `^[a-z][a-z0-9_.-]*$`. Die Registry beschreibt
dieselben korrigierten IDs wie der private Producer. Der zuvor
festgestellte Grossbuchstabenfehler im T50-Vorbereitungspfad besteht nicht
mehr.

T50 bleibt an `valid_cell("H1", "TSPM1")` gebunden. Die Quellkette ueber
Registry, Frame, Envelope, TSPM-Bindung, Ergebnisaufbau und Budgetvalidator
wurde gelesen, nicht ausgefuehrt. Die unveraenderte Mutation setzt
`formation_write_counts` bei Index 1 auf 294 bei Grenze 293 und Rest -1.
Der Budgetkonstruktor akzeptiert die arithmetisch konsistente Belegform;
`validate_s2dr_cell_result` bleibt der relationale Ablehnungsort mit
`S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED`.

Die bestehenden Digestfunktionen beziehen die geaenderten ID-Payloads
ein. Registry-/Fixture-/Plandigests sowie Frame-/Envelope-Digests werden
bei einer spaeter freigegebenen Erzeugung daraus neu abgeleitet. Alte
Ergebnisbelege werden weder umgedeutet noch auf neue Quellen umgeschrieben.
In diesem Audit wurden keine Registry oder Ergebnisobjekte erzeugt.

### Unveraendertheit und Abdeckung

Die AST-Differenz zeigt genau vier ergaenzte `.lower()`-Aufrufe in
Formatierungen von `history_id`. Nach rein syntaktischem Entfernen dieser
Normalisierung sind alter und neuer Modul-AST identisch.

R0-Typen und -Operatoren, R0-Projektion, Comparator, Owner, Receipt- und
Budgetvalidatoren sind unveraendert. Die Testdatei ist unveraendert und
enthaelt weiterhin 51 Definitionen T01-T51, darunter zwoelf
Fail-Closed-Faelle. Der reparierte Rueckgabeblock und die Comparatorpfade
T35-T39/T51 bleiben erhalten; ebenso T44 und die S1WU-Findingbindung.

PPB-1, TSPM-1-Grundkern, Rezeptorvertrag, API, Snapshot, Produktion und
Feldpfad wurden nicht veraendert. Beide privaten Dateien sind per AST
parsebar. Git-Differenz und Quellenhashes binden den geprueften Bestand.

## Entscheidung und Grenze

S2-EA: `SCOPED_SOURCE_ID_CORRECTION_COMPLETE`.
S2-DX: `PASS_STATIC_IMPLEMENTATION_AND_TEST_AUDIT_AFTER_S2EA`.

Im freigegebenen Wiederholungsumfang verbleibt kein identifizierter
statischer Blocker. Dies ist keine Aussage, dass 51 Tests bereits bestanden
sind, und kein Vergleichs- oder Memory-Befund. Ausfuehrungsfehler koennen
erst durch einen gesondert freigegebenen Testlauf beurteilt werden.

Naechster Schritt: separate Freigabe fuer S2-EB zur Ausfuehrung der 51
gebundenen synthetischen Vertragstests. Dieser Audit fuehrt keinen Test
aus und erteilt selbst keine Ausfuehrungsfreigabe. Die registrierte
56-Zellen-Vergleichsmatrix, Produktion und Feldintegration bleiben gesperrt.
