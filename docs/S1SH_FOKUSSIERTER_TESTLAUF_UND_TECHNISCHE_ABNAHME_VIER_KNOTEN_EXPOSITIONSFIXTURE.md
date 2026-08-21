# S1-SH: Fokussierter Testlauf und technische Abnahme des Vier-Knoten-Expositionsfixtures

## Status und Umfang

S1-SH fuehrt genau den in S1-SG gebundenen unveraenderten fokussierten
Testlauf des kanonischen 17-Plan-Expositionsfixtures aus. Zwischen
Implementierungscommit und Lauf wurden Produktions- und Testquelle nicht
veraendert.

Abnahmeentscheidung:

```text
THIRTEEN_OF_THIRTEEN_EXPOSURE_FIXTURE_TESTS_PASSED
CANONICAL_SEVENTEEN_PLAN_FIXTURE_TECHNICALLY_ACCEPTED
PREFIX_LOAD_TIME_AND_U_PAIR_IDENTITIES_TECHNICALLY_ACCEPTED
FAIL_CLOSED_FIXTURE_VALIDATION_TECHNICALLY_ACCEPTED
NO_ALIGN_APPLICATION_NO_MODEL_INVOCATION_NO_MATRIX_CELL
```

## Ausgefuehrter Befehl

```text
python -m unittest discover -s tests -p "test_four_node_exposure_fixture.py" -v
```

Ergebnis:

```text
Ran 13 tests in 0.270s
OK
```

Der Prozess endete mit Exitcode `0`.

## Vorlaufidentitaet

Der Lauf startete aus Commit `ec57c56`. Der Arbeitsbaum war leer, und
Produktions- sowie Testquelle waren gegen diesen Commit unveraendert. Vor
dem Lauf wurden genau 13 Testmethoden gezaehlt.

Der gebundene Befehl wurde einmal ohne Korrektur oder Wiederholung
ausgefuehrt.

## Technisch abgenommene Oberflaeche

Innerhalb der fokussierten Tests sind bestaetigt:

- die registrierte 17-Plan-Achse;
- exakt 127 synchrone Modellintervalle, 17 Alignereignisse und 40 passive
  Checkpoints pro Modellrolle;
- deterministische Konstruktion und rekursive Unveraenderlichkeit;
- Fixturedigest
  `ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e`;
- Kontaktwerte, Carrierordnung, Feldclock und Ein-Sekunden-Grenzen;
- leere Nullkontaktverteilungen ohne Nullframe;
- Snapshotidentitaeten ohne Plan- oder Modelllabels;
- echte T-Praefixe und eine davon verschiedene F-Geschichte;
- F- sowie lokale/entfernte Last- und Zeitanpassung;
- nur passive C-Zusatzcheckpoints;
- unterschiedlicher I- und frueher Freigabe-Gap sowie echter
  frueher/spaeter Gap-Praefix;
- wert- und zeitidentische B-/Probeinputs innerhalb des fruehen und spaeten
  U-Paars;
- zeitfreie Align- und Checkpointereignisse;
- Annahme nur des kanonischen Fixtures;
- fail-closed Ablehnung geaenderter Planachse und ungueltiger
  Matrixregistrierung.

## Nicht geprueft

S1-SH prueft ausdruecklich nicht:

- die Anwendung des Alignziels auf einen realen Feldcarry;
- die bitgleiche Erhaltung privater Zustaende waehrend Align und
  Checkpoints;
- einen Modellaufruf oder Carryfortschritt entlang eines Plans;
- die atomare Ausfuehrung einer einzelnen Matrixzelle;
- die Kreuzung aller 238 Zellen;
- Comparatoren, Baselineergebnisse oder Feldentwicklung;
- eine Faehigkeit einer hypothetischen MCM-Memory-Entwicklungsrichtung.

## Technische Bewertung

Das gemeinsame Expositionsfixture ist innerhalb seiner fokussierten
Testoberflaeche technisch abgenommen. Der naechste Engpass liegt nicht mehr
in Werten oder Planform, sondern in der aeusseren Lebenszyklushuelle: Sie
muss Modellintervalle, zeitloses Align und passive Checkpoints verbinden,
ohne privaten Carry oder Feldzeit waehrend aeusserer Operationen zu
veraendern.

Vor einer Implementierung muss insbesondere geklaert werden, wie nach einer
reinen S/H-/Kontaktprojektion ein vollstaendig gueltiger neuer
`FourNodeModelCarry` gebildet wird, ohne private Identitaeten neu zu
materialisieren oder historische Provenienz zu verlieren.

## Aussagegrenze

Der bestandene Testlauf ist eine technische Fixtureabnahme. Er ist kein
Feldlauf, kein Baselinevergleich und kein Befund einer hypothetischen
MCM-Memory-Entwicklungsrichtung.

## Genau ein naechster Schritt

S1-SI ist ausschliesslich als statischer Vier-Knoten-Align-, passiver
Checkpoint- und atomarer Einzelzellen-Lebenszyklusvertrag zulaessig.

S1-SI muss Einfuegepunkte, erlaubte Feldprojektion, Carry-Neubindung,
Privatstatus- und Feldzeiterhaltung, Checkpointform, Ereignisfortschritt und
Abbruchregeln binden. Keine Implementierung, kein Test, kein Modelllauf,
keine Matrixzelle und kein Forschungslauf.
