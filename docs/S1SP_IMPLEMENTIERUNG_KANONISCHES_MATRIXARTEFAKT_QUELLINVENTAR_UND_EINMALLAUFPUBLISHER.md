# S1-SP: Implementierung von Matrixartefakt, Quellinventar und Einmallaufpublisher

## Status

S1-SP setzt ausschliesslich den in S1-SO gebundenen technischen
Persistenz- und Einmallaufpfad um. Es wurde keine Testmethode ausgefuehrt,
keine reale Zelle erzeugt und keine reale 238-Zellen-Matrix gestartet.

## Matrixresultatvalidator

`four_node_matrix_lifecycle.py` stellt nun die reine oeffentliche Rolle

```text
validate_four_node_matrix_result
```

bereit. Sie ruft keinen Producer auf. Fuer ein abgeschlossenes Resultat
rekonstruiert sie die feste Plan-/Rollenordnung, alle 560
Checkpointdigests, die 238 Summarydigests, die Matrixdigestkette, die
Rollenkonfigurationen, die Budgetidentitaet und den Matrixresultatdigest.
Eine Abweichung wird nicht repariert.

## Kanonisches Ergebnisartefakt

`four_node_matrix_artifact.py` implementiert die strikte Projektion eines
vollstaendigen `FourNodeMatrixResult` in das gebundene ASCII-JSON-Schema.
Der Parser verlangt:

- exakt bekannte Felder und eindeutige JSON-Schluessel;
- kanonische Bytegleichheit samt abschliessendem LF;
- gueltige Quell-, Eingabe-, Summary-, Checkpoint-, Ketten-, Matrix- und
  Artefaktdigests;
- die feste Schema-, Vertrags-, Ausfuehrungs- und Autorisierungsidentitaet;
- ausschliesslich carryfreie Summary- und Checkpointprojektionen.

Private Payloads, finale Carryobjekte, Comparatorwerte und
Ergebnisinterpretationen werden nicht in das Artefakt aufgenommen.

## Lokales Quellinventar

Das Quellinventar startet an den drei in S1-SO gebundenen Produktionsrollen
und erfasst zusaetzlich `mcm_field_organism/__init__.py`, weil dieser
Paket-Bootstrap bei `python -m` vor dem Runner ausgefuehrt wird. Danach wird
die transitive lokale Importmenge per AST aufgeloest und byteweise
SHA-256-gebunden.

Die statische Implementierungskontrolle konnte den aktuellen Abschluss
vollstaendig aufloesen. Er umfasst 93 erreichbare lokale Produktionsdateien.
Ein konkreter finaler Inventardigest wird in S1-SP noch nicht als
Realpreflightidentitaet gebunden; diese Bindung gehoert erst nach der
synthetischen Abnahme in S1-SR.

## Einmallaufpublisher

`four_node_matrix_single_run.py` akzeptiert nur die feste Autorisierung und
die vier festen Reportpfade. Vor dem Producer werden Manifest,
Matrixregistrierung, Fixture, Eingabedateien und Quellinventar validiert.
Danach entstehen Sperre und Versuchsnachweis exklusiv und datentraeger-
bestaetigt.

Im Produktionsmodul existiert genau eine lexikalische Aufrufstelle fuer
`execute_four_node_matrix`. Nach ihrer Rueckkehr werden Matrixresultat,
Quellen und Eingabedateien erneut geprueft. Das Ergebnis wird erst nach
kanonischem Staging-Roundtrip durch einen exklusiven gleichverzeichnisigen
Hardlink sichtbar. Ein gestarteter Fehler hinterlaesst Sperre und
Versuchsnachweis, aber kein Ergebnis und keine Teilmatrix. Es gibt keinen
Retry-, Resume- oder automatischen Gitpfad.

## Definierte synthetische Tests

`tests/test_four_node_matrix_artifact_and_single_run.py` enthaelt exakt 18
Testmethoden. Sie pruefen statisch vorgesehen:

- vollstaendige Matrix-, Summary- und Checkpointdigestvalidierung;
- deterministische kanonische Artefaktbytes und strikten Roundtrip;
- unbekannte, fehlende, doppelte und nichtkanonische JSON-Felder;
- Carry- und Privatpayloadausschluss;
- deterministisches lokales Quellinventar und feste Eingabedateiachse;
- Autorisierung und Vorstartabbruch ohne Laufbelege;
- exklusiven Wiederholungsschutz;
- genau einen synthetischen Matrixproducer-Aufruf;
- gestarteten Fehler und Vor-/Nachlauf-Quelldrift ohne Ergebnis;
- kanonische Attempt-/Lockdigests und Erfolgscleanup;
- fehlende Unterprozess-, Thread-, Netzwerk-, Git- und Comparatorpfade.

Alle Runnerpruefungen ersetzen `execute_four_node_matrix` durch ein
synthetisches Testdouble. Keine Testmethode darf den realen Zellproducer
oder die reale Matrix aufrufen.

## Statische Kontrolle

Die vier gebundenen Python-Dateien sind syntaktisch kompilierbar. Die neue
Testdatei enthaelt exakt 18 Testmethoden. Der AST-Quellabschluss ist ohne
dynamische oder unaufloesbare lokale Importkante bestimmbar.
`git diff --check` meldete keine Inhaltsfehler.

Keine Testmethode, keine reale Zelle und keine reale Matrix wurde
ausgefuehrt.

## Entscheidung und Grenze

```text
CANONICAL_MATRIX_ARTIFACT_SOURCE_INVENTORY_AND_ONE_SHOT_PUBLISHER_IMPLEMENTED
EIGHTEEN_SYNTHETIC_TESTS_DEFINED_NOT_RUN
NO_REAL_CELL_NO_REAL_MATRIX_NO_RESULT_DECISION
```

S1-SP ist als Implementierung abgeschlossen, aber nicht technisch
abgenommen. Der einzige naechste Schritt ist S1-SQ: genau ein
unveraenderter fokussierter Lauf von
`tests/test_four_node_matrix_artifact_and_single_run.py`. Bei einem Fehler
wird ohne Reparatur oder Wiederholung gestoppt. Der reale Einmallauf bleibt
auch danach bis zum statischen S1-SR-Realpreflight und einer gesonderten
S1-SS-Freigabe gesperrt.
