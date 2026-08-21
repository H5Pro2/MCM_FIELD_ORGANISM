# S1-SW: Einmaliger synthetischer Comparator-Testlauf und technische Abnahme

## Ausfuehrungsumfang

S1-SW fuehrte genau einmal und unveraendert ausschliesslich den in S1-SV
gebundenen synthetischen Testkatalog aus:

```text
python -m unittest tests.test_four_node_baseline_reference_comparator
```

Es wurden keine weiteren Tests, kein Modellproducer und keine numerische
Auswertung des realen S1-SS-Artefakts aufgerufen. Ein Retry fand nicht
statt.

## Ergebnis

```text
...................
----------------------------------------------------------------------
Ran 19 tests in 0.865s

OK
```

Damit sind im synthetisch gebundenen Umfang technisch abgenommen:

- die feste Vertragsidentitaet und die vollstaendigen Ausgangsachsen;
- 322 geordnete Rohkontraste und 91 vollstaendige Profilpaare;
- signed Links-minus-rechts-Residuen und 320-Komponenten-Paarresiduen;
- die symmetrische relative Profilmetrik und feste Profilgrenze;
- C-Deltabildung und die diagnostische U-Zuordnung;
- Fail-Closed-Verhalten bei Achsen-, Provenienz-, Angleichungs-, Digest-
  und Zahlenfehlern;
- die Trennung der reinen Vergleichsschicht von Runner, Modellkern,
  Fixture und Lifecycle.

`OK` ist ausschliesslich die technische Abnahme dieser synthetischen
Pruefungen. Es ist kein Baselinebefund, kein Kandidatenbefund und kein
Funktionsnachweis fuer eine hypothetische MCM-Memory-Entwicklungsrichtung.

## Verbindliche Entscheidung

```text
SYNTHETIC_BASELINE_REFERENCE_COMPARATOR_TESTS_ACCEPTED
19_OF_19_TESTS_PASSED_ON_FIRST_AND_ONLY_RUN
NO_REAL_ARTIFACT_EVALUATION
NO_CANDIDATE_NO_FUNCTIONAL_DECISION
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-SX als statischer Vertrag fuer den
realen passiven Comparatorpfad. Vor jeder realen Zahlenoperation sind
Eingabedateien, Quellinventar, Aufruf, kanonisches Ergebnisformat,
atomare Publikation, Vorstartschutz, Fehlerbeleg und Wiederholungssperre zu
binden.

S1-SX darf noch keinen realen Comparator aufrufen, keine Ergebnisdatei
anlegen und keine Modell- oder Funktionsentscheidung treffen.
