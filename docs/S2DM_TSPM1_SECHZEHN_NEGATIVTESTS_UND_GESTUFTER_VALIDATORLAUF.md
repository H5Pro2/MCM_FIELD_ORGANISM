# S2-DM: TSPM-1-Negativtests und gestufter Validatorlauf

## Auftrag und Grenze

S2-DM implementiert ausschliesslich die in S2-DL gebundene private
Testdatei `tests/test_tspm1_s2dm_negative_contract.py`. Sie enthaelt genau
16 Einzeltests fuer die vier Prioritaets-, acht Relations-, drei
PPB-1-Abnahme- und einen Atomaritaetsfall.

TSPM-1, PPB-1, bestehende Tests, API, Snapshot und Feldpfad wurden nicht
geaendert. Es gab keine Produktions- oder Feldausfuehrung. Der Befund ist
ausschliesslich ein technischer Validatorbefund.

## Quellenbindung

Die statische Vorpruefung bestaetigte vor der Ausfuehrung:

- privater TSPM-1-Quelldigest:
  `c33ea3fdbc399b88e1416e91f8421f362060de1e368817e3673a93c522013252`;
- unveraenderter S2-DH-Testdigest:
  `836bd2a6ed663590eb2bcbe17442d2bc2e9bab8f2032c34208953dae50b3865d`;
- unveraenderter PPB-1-Quelldigest:
  `9fad3b04661fb9b8da053afd5599e3bdfe73019681ae50115263c39f3052ca9d`;
- S2-DM-Testdigest:
  `6397d5b48c5f98c1da6471e83239aab663e49b1fd1e27111b47497fe55788797`;
- exakt 16 statisch erkennbare Testmethoden `P01` bis `P04`, `R05` bis
  `R12`, `B13` bis `B15` und `A16`.

## Einmalige Ausfuehrung

Die gebundene Stufenfolge wurde ohne Wiederholung angestossen:

1. Neue Negativtests: `16/16` bestanden.
2. Direkter TSPM-1-Umfang: `27/27` bestanden.
3. Fokussierter Gesamtumfang: einmal angestossen; die Werkzeugausgabe wurde
   wegen ihrer Groesse abgeschnitten und ist keiner abrufbaren
   Terminalsitzung zugeordnet.

Fuer die dritte Stufe liegt deshalb kein reproduzierbarer Abschlussbeleg mit
Exitcode und Testsumme vor. Sie wird nicht nachtraeglich als `76/76`
interpretiert und gemaess der ausdruecklichen Retry-Sperre nicht wiederholt.

## Fail-Closed-Entscheidung

`INCOMPLETE_TSPM1_VALIDATOR_STAGE3_RESULT_UNAVAILABLE_NO_RETRY`

Die 16 neuen Negativtests und der direkte 27er-Umfang sind technisch
bestanden. Der S2-DM-Gesamtabschluss ist jedoch nicht belegt, weil die
Abschlussstufe nicht beweissicher ausgewertet werden kann. Daraus folgt
weder ein Memory-Befund noch ein MCM-Feldnachweis.

## Naechster Schritt

S2-DN darf nur nach ausdruecklicher fachlicher Entscheidung festlegen, wie
mit der unbelegten dritten Stufe umzugehen ist. Ohne neue Freigabe bleiben
eine Wiederholung, weitere Tests sowie jede API-, Snapshot-, Produktions-
oder Feldintegration gesperrt.
