# S1-CL: E1 E4 Lazy-Runnerinventar und statische Matrixbereitschaft

## Status

Das vollstaendige E4-Runnerinventar ist als lazy, schreibgeschuetzte und
streng geordnete Verdrahtung implementiert und statisch abgenommen.

Beim Aufbau des Inventars wurde kein Modellrunner ausgefuehrt. Weder
`compose_e1_e4_run_result(...)` noch `evaluate_e1_e4_run(...)` werden durch
den Inventarcode importiert oder aufgerufen. Es existiert weiterhin keine
E4-Gesamtmatrix und keine E4-Entscheidung.

## Implementierung

```text
mcm_field_organism/e1_e4_runner_inventory.py
tests/test_e1_e4_runner_inventory.py
```

Die Rollen bleiben privat und sind nicht ueber Paketwurzel oder
`current_api` erreichbar.

## Inventar

Die schreibgeschuetzte Abbildung besitzt exakt diese Reihenfolge:

```text
e1, b0, b1, b2, b3, b4, b5, b6, oracle-g
```

Die Bindungen sind:

```text
e1/b0/b1  gemeinsamer gecachter S1-CJ-Produzent
b2        isolierter S1-CK-S2-B2-Runner
b3-b6     vier S1-CI-F3-Familienrunner
oracle-g  aus dem gecachten, Fixed-Gain-validierten E1-Run
```

E1, B0 und B1 werden bei spaeterer Ausfuehrung gemeinsam genau einmal
erzeugt und danach aus einem privaten Cache gelesen. ORACLE-G verwendet
denselben gecachten E1-Run. Dies verhindert drei voneinander abweichende
E1-Historien innerhalb einer spaeteren Matrix.

Die S1-CD-Kontinuitaetsanker besitzen einen getrennten lazy Lieferanten. Er
teilt denselben E1-Cache und wird beim Inventaraufbau nicht ausgewertet.

## Statischer Digest

Inventarreihenfolge, Factoryidentitaeten, Feld- und E1-Geometrie,
E1-Vertrag, S/H-Zeitparameter und Ankernamen sind in einem SHA-256-Digest
gebunden:

```text
e76d4154ed6e9d68a68b770c2df26012e63ca1abc02149b7c29b8b2a0c1c25c1
```

Eine Aenderung dieser statischen Verdrahtung muss den Digest aendern und
macht eine vorhandene Ausfuehrungsfreigabe ungueltig.

## Abnahmegrenzen

Die Suite instrumentiert die E1-, S2- und Oracle-Funktionen und bestaetigt,
dass sie beim Inventaraufbau nicht aufgerufen werden. Die vier F3-Factorys
erzeugen nur Callables; ihre isolierte Nichtausfuehrungsgrenze wurde bereits
in S1-CI geprueft.

Das Inventar akzeptiert nur:

- ein frisches, noch nicht fortgeschriebenes Feld;
- einen geometriegleichen neutralen E1-Anfangszustand;
- `response_time_seconds = 1.0`;
- `afterimage_time_seconds = 0.5`;
- exakt neun bekannte Runner ohne Zusatzrolle.

## Technische Abnahme

Fokussiert:

```text
python -m unittest -v tests.test_e1_e4_runner_inventory

8 tests
OK
```

Gemeinsam mit allen isolierten E4-Runnern und ihren relevanten
Bestandsvertraegen, jedoch ohne S1-BZ und S1-CD:

```text
96 tests
OK
```

Geprueft wurden:

- exakte Modellreihenfolge und vollstaendiger Preflight;
- keine Runnerausfuehrung beim Aufbau;
- keine Referenz auf Komposition oder Entscheidung;
- schreibgeschuetztes Inventar;
- deterministischer fest gebundener Inventardigest;
- Ablehnung geaenderter Zeitparameter und nichtneutraler E1-Eingabe;
- unveraenderte Eingaben und private API-Grenze.

## Aussagegrenze

S1-CL bestaetigt nur statische Matrixbereitschaft. Die Runner wurden in
frueheren Schritten einzeln abgenommen, aber noch nicht gemeinsam in einem
E4-Ergebniscontainer ausgefuehrt oder verglichen. Es folgt kein
Memory-, Lern-, Organisations-, Semantik- oder KI-Befund.

## Bester naechster Schritt

S1-CM registriert vor jeder Ausfuehrung den einmaligen Aufrufweg vom
festen Inventardigest ueber Runner, Ankerlieferant und Ergebniscontainer bis
zur externen Entscheidung. Er bindet Ausgabedatei, atomare Speicherung,
Ergebnisdigest, Fehlerverhalten und das Verbot einer Wiederholung. S1-CM
fuehrt den E4-Lauf noch nicht aus.
