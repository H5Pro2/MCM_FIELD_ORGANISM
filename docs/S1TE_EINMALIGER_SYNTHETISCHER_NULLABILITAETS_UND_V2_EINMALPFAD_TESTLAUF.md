# S1-TE: Einmaliger synthetischer Nullabilitaets- und v2-Einmalpfad-Testlauf

## Ausfuehrungsumfang

S1-TE fuehrte genau einmal und unveraendert ausschliesslich den in S1-TD
angepassten synthetischen Testkatalog aus:

```text
python -m unittest tests.test_four_node_baseline_reference_artifact_and_single_run
```

Es wurden keine weiteren Tests, kein reales S1-SS-Comparing und kein
Modellproducer aufgerufen. Ein Retry fand nicht statt.

## Ergebnis

```text
....................
----------------------------------------------------------------------
Ran 20 tests in 4.751s

OK
```

Im synthetisch gebundenen Umfang sind damit technisch abgenommen:

- vollstaendig numerische R-Provenienz;
- vollstaendig all-null R an der gebundenen C-Gap-Lage;
- Ablehnung gemischter oder falsch platzierter Nullabilitaet;
- Ablehnung von `None` in S und H;
- Trennung von Kontaktabwesenheit und explizitem Nullkontakt;
- kanonischer JSON-`null`-Roundtrip;
- unveraenderte vollstaendige Profil- und Paarprovenienz;
- neue S1-TG-v2-Schema-, Autorisierungs- und Pfadidentitaet;
- Koexistenz erhaltener S1-TB-Belege mit freien S1-TG-Pfaden;
- Einmalschutz, Driftstopp und atomare Publikationsfehlergrenze.

`OK` ist ausschliesslich die technische synthetische Abnahme. Es ist kein
realer Baselineatlas, kein Kandidatenbefund und kein Funktionsnachweis fuer
eine hypothetische MCM-Memory-Entwicklungsrichtung.

## Verbindliche Entscheidung

```text
SYNTHETIC_NULLABLE_RECEPTOR_PROVENANCE_AND_V2_ONE_SHOT_PATH_ACCEPTED
20_OF_20_TESTS_PASSED_ON_FIRST_AND_ONLY_RUN
S_H_METRICS_UNCHANGED_NO_REAL_COMPARATOR
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-TF als letzter rein statischer
v2-Realpreflight. Er muss den sauberen Gitstand, das zweimal identische neue
Quellinventar, die drei Eingabebytes, exakt 14 nullable R-Records, 14 mal 40
Checkpoints, freie S1-TG-Pfade, bytegleiche S1-TB-Belege, Laufzeit,
Aufrufstelle und autorisierten v2-Befehl konkret binden.

S1-TF darf keinen Test wiederholen, keinen Comparator aufrufen und keine
Laufdatei anlegen. Erst nach bestandenem S1-TF ist S1-TG als neuer,
getrennter Einmallauf zulaessig.
