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
3. Fokussierter Gesamtumfang: Der erste Lauf wurde angestossen, seine
   Werkzeugausgabe aber abgeschnitten und keiner abrufbaren Terminalsitzung
   zugeordnet. Er wurde deshalb nicht als bestanden interpretiert.
4. Nach ausdruecklicher einmaliger Freigabe wurde ausschliesslich die dritte
   Stufe erneut ausgefuehrt. Die Stufen 1 und 2 wurden nicht wiederholt. Der
   Abschlusslauf bestand `76/76` Tests mit Exit-Code `0`, 76 vollstaendigen
   Erfolgszeilen und terminalem `OK`.

Der vollstaendige atomar veroeffentlichte Ergebnisbeleg liegt unter
`reports/s2dm_tspm1_76_test_closure_v1.json`. Sein SHA-256-Digest lautet
`8c9a363ca8081ec680d9eb28826884f980d75a1d917534709e596f42c94659b3`.
Er bindet die vollstaendige Runnerausgabe, Testsumme, Exit-Code, Fehlercodes,
Owner-Endzustaende, PPB-1-Aufrufbudgets und unveraenderten Quelldigests.

## Fail-Closed-Entscheidung

`PASS_TSPM1_PRIVATE_VALIDATOR_NEGATIVE_CONTRACT_76_OF_76`

Die 16 neuen Negativtests, der direkte 27er-Umfang und der fokussierte
76er-Abschluss sind technisch bestanden. Die S2-DK-Validator- und
Pruefreihenfolgekorrektur ist damit innerhalb des gebundenen privaten
Umfangs abgenommen. Daraus folgt weder ein Memory-Befund noch ein
MCM-Feldnachweis.

## Naechster Schritt

S2-DN kann nach separater Freigabe ausschliesslich als statischer
Abschlussaudit die Quellenbindung, Ergebnisdatei, atomare Veroeffentlichung
und unveraenderten privaten Grenzen von S2-DM abnehmen. Keine erneute
Testausfuehrung und keine API-, Snapshot-, Produktions- oder Feldintegration
sind dadurch freigegeben.
