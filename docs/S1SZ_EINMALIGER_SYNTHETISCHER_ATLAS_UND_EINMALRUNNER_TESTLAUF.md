# S1-SZ: Einmaliger synthetischer Atlas- und Einmalrunner-Testlauf

## Ausfuehrungsumfang

S1-SZ fuehrte genau einmal und unveraendert ausschliesslich den in S1-SY
gebundenen synthetischen Testkatalog aus:

```text
python -m unittest tests.test_four_node_baseline_reference_artifact_and_single_run
```

Es wurden keine weiteren Tests, kein reales S1-SS-Comparing und kein
Modellproducer aufgerufen. Ein Retry fand nicht statt.

## Ergebnis

```text
....................
----------------------------------------------------------------------
Ran 20 tests in 5.821s

OK
```

Im synthetisch gebundenen Umfang sind damit technisch abgenommen:

- vollstaendige 14-Profil- und 91-Paarprovenienz;
- Ablehnung manipulierter Profil-, Paar- und Resultatidentitaeten;
- deterministische kanonische Artefaktbytes und strikter Roundtrip;
- Erhalt aller signed Profile, Kontraste und Paarresiduen;
- transitives lokales Quellinventar und feste Dreier-Eingabeachse;
- Vorstartschutz und feste Laufpfade;
- genau ein synthetisch ersetzter Comparatoraufruf;
- persistente Belege bei gestartetem Fehler;
- Quelldrift- und Hardlinkfehler ohne Teilresultat;
- fehlende direkte Modellproducerimporte und einzige CLI-Autorisierung.

`OK` nimmt ausschliesslich den synthetischen technischen Pfad ab. Es ist
kein realer Baselineatlas, kein Kandidatenbefund und kein Funktionsnachweis
fuer eine hypothetische MCM-Memory-Entwicklungsrichtung.

## Verbindliche Entscheidung

```text
SYNTHETIC_BASELINE_REFERENCE_ATLAS_AND_ONE_SHOT_PATH_ACCEPTED
20_OF_20_TESTS_PASSED_ON_FIRST_AND_ONLY_RUN
NO_REAL_COMPARATOR_NO_MODEL_PRODUCER_NO_FUNCTIONAL_DECISION
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-TA als letzter rein statischer
Realpreflight. Er muss den sauberen Gitstand, das konkrete transitive
Comparator-Quellinventar, alle drei Eingabebytes und semantischen
Identitaeten, fehlende Laufpfade, Laufzeitidentitaet, exakt eine
Comparator-Aufrufstelle sowie den unveraenderten autorisierten Befehl
binden.

S1-TA darf keinen Test wiederholen, keinen Comparator aufrufen und keine
Laufdatei anlegen. Erst nach bestandenem S1-TA kann eine gesonderte
Einmallauffreigabe fuer S1-TB fachlich beurteilt werden.
