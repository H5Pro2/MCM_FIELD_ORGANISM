# Synaptischer Memory-Lebenszyklus: Negativbefund

## Frage

Kann der unveränderte passive Zwei-Zeitlagen-Synapsenkandidat eine lokale
Beziehung aufbauen, während längerer Unterbrechung vollständig lösen und
anschließend andere Feldwirkung binden?

## Weltverlauf

```text
4 Phasen Kontakt A
8 Phasen Unterbrechung
4 Phasen Kontakt B
```

Jede Phase dauert eine Sekunde und durchläuft die vorhandenen Audio- und
Videorezeptoren sowie das unveränderte gemeinsame MCM-Feld. Der Kandidat bleibt
passiv und schreibt nicht in die Runtime zurück.

Vergleichsbaseline ist die bereits verwendete Zwei-Leaky-Kaskade mit denselben
schnellen und langsamen Raten.

## Ergebnis

```text
lokale Beziehungen insgesamt                  290
vom Kandidaten aufgebaute Beziehungen          290

Kandidat nach Aufbau                      0,003682
Kandidat nach Unterbrechung                0,004225
alter Rest relativ zum Aufbau                1,1476
alte Beziehungen vollständig gelöst           nein
Änderung durch Kontakt B                   0,003230

Zwei-Leaky nach Aufbau                    0,003495
Zwei-Leaky nach Unterbrechung              0,003416
alter Rest relativ zum Aufbau                0,9773
alte Beziehungen vollständig gelöst           nein
Änderung durch Kontakt B                   0,002995

maximale lokale Budgetnutzung              0,117670
vorgegebenes lokales Budget                0,800000
```

Der Lauf ist exakt reproduzierbar. Rohsensordaten werden nicht behalten und
der Organismuszustand wird nicht verändert.

## Befund

Der Kandidat bildet keine selektive Feldtopologie. Die positive
amplitudenbasierte Koaktivität des diffundierenden Feldes prägt alle 290
vorhandenen lokalen Nachbarschaften.

Während der Unterbrechung löst sich die alte stabilisierte Lage nicht. Sie
steigt sogar auf rund `114,8 %` ihres Aufbauwertes, weil die flexible Lage noch
weiter stabilisierend wirkt. Auch die Zwei-Leaky-Baseline löst nicht
vollständig.

Kontakt B verändert beide Systeme in ähnlicher Größenordnung. Das lokale Budget
trägt den Verlauf nicht, weil es mit höchstens `0,117670` weit unter seiner
Grenze bleibt.

## Entscheidung

Der amplitudenbasierte Zwei-Zeitlagen-Synapsenkandidat wird verworfen.

Nicht freigegeben werden:

- Runtime-Rückwirkung,
- adaptive Feldkopplung,
- Parameteroptimierung,
- Schwellen für funktionales Vergessen,
- nachträgliche Gewinner- oder Auswahlregeln.

Eine Ratenanpassung würde die fehlende Selektivität und vollständige Lösung
nicht begründen, sondern nur den vorliegenden Weltverlauf passend einstellen.

## Offene Anschlussfrage

Vor einem neuen Kandidaten ist konzeptionell zu klären:

> Kann lokale zeitliche Ursache oder Reihenfolge eine Beziehung selektiv
> prägen, ohne bloße Amplitudenkoaktivität, feste Schwelle, globalen Gewinner
> oder vorgegebene Zieltopologie?

Bis diese Frage eine neutrale lokale Zustandsrolle begründet, bleibt organisches
Memory in der Runtime geschlossen.
