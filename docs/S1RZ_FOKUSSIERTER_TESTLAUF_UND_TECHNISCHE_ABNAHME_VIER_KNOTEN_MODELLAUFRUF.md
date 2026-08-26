# S1-RZ: Fokussierter Testlauf und technische Abnahme des Vier-Knoten-Modellaufrufs

## Status und Umfang

S1-RZ fuehrt exakt den in S1-RY gebundenen unveraenderten Testlauf der
gemeinsamen Vier-Knoten-Aufrufoberflaeche aus. Zwischen Implementierungscommit
und Lauf wurden Produktionsquelle und Testdatei nicht veraendert.

```text
ELEVEN_OF_ELEVEN_INVOCATION_TESTS_PASSED
FOURTEEN_SYNCHRONOUS_ROLE_PATHS_TECHNICALLY_ACCEPTED
ELEVEN_TRANSIENT_ROLE_PATHS_TECHNICALLY_ACCEPTED
THREE_SYNC_ONLY_GATES_TECHNICALLY_ACCEPTED
ATOMIC_CARRY_AND_FAILURE_SURFACE_ACCEPTED
```

## Ausgefuehrter Befehl

```text
python -m unittest discover -s tests -p "test_four_node_model_invocation.py" -v
```

Ergebnis:

```text
Ran 11 tests in 6.873s
OK
```

Der Prozess endete mit Exitcode `0`.

## Technisch abgenommene Oberflaeche

Innerhalb der fokussierten Tests sind bestaetigt:

- ein vollstaendiger synchroner Vier-Knoten-Aufruf aller 14 Rollen;
- ein vollstaendiger transienter Aufruf aller elf dafuer zugelassenen Rollen;
- `NOT_COMPUTABLE` fuer transiente B1-, B2- und M4-Aufrufe vor Kernausfuehrung;
- vollstaendiger Carry als einzige Quelle eines zweiten Intervalls;
- Feldzeitfortschritt von Tick null ueber zwei lueckenlose Intervalle;
- exakt eine B3-M-Quelle im Folgefeld und privaten Wrapper;
- unveraenderter B1-Festadaptercarry und vollstaendiger B2-L-Folgezustand;
- vollstaendige M4-Folgeanatomie ohne Kandidatensidecar;
- Refinementpflicht nur fuer B3-B6;
- atomare Kernfehlerkapselung ohne Feld, Privatstatus oder Teilcarry;
- deterministische Ergebnis- und Carrydigests;
- fehlende historische Adapter-, Materializer- und Orchestratorimporte.

## Architekturstand

Die technisch abgenommene konstruktive und aufrufbare Kette lautet nun:

```text
validiertes S1-RK-Manifest
  -> isoliertes rollenweises Vier-Knoten-Frischbundle
  -> technisch abgenommene Modelleingangsmontage
  -> rollenfester atomarer Modellaufruf
  -> vollstaendiger Folgecarry oder NOT_COMPUTABLE
```

Damit ist die Rollenverdrahtung technisch geschlossen. Noch nicht gebunden
ist eine konkrete gemeinsame Ereignisgeschichte fuer die 16
S1-RA-Expositionsrepliken.

## Methodische Folgerung

B1, B2 und M4 sind nur synchron anschliessbar. Eine vollstaendige
14-mal-16-Pflichtmatrix kann deshalb nur ausgefuehrt werden, wenn alle
modellwirksamen S1-PZ-Segmente als normale synchrone
`ReceptorDistribution`/`MCMFieldStepTime`-Intervalle materialisiert werden.

Dies ist zulaessig, weil S1-RA fuer Kontakt- und Gap-Geschichten keine
transiente Kernform vorschreibt. Es muss jedoch vor jeder Orchestrierung
statisch und fuer alle Rollen gemeinsam gebunden werden. Eine spaetere
rollenabhaengige Wahl der Intervallform waere kein fairer Vergleich.

## Nicht geprueft

S1-RZ prueft keine der 16 Expositionsrepliken, keine 224-Zellen-Matrix,
keinen Checkpoint, keinen Comparator und keine Funktionsprognose. Die
Einzelintervalle sind technische Integrationspruefungen und kein Befund zu
einer hypothetischen MCM-Memory.

## Paketstatus

```text
S1RZ_FOUR_NODE_MODEL_INVOCATION_TECHNICALLY_ACCEPTED
FOURTEEN_ROLE_EXECUTION_PATHS_AVAILABLE
COMMON_SIXTEEN_REPLICA_EXPOSURE_FIXTURE_NOT_BOUND
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

```text
S1-SA - statischer gemeinsamer synchroner Vier-Knoten-Expositionssegment-,
        Ereignisplan- und 16-Repliken-Fixturevertrag
```

S1-SA muss konkrete gemeinsame Kontakt- und Nullkontaktsegmente, Feldzeiten,
Knotenvektoren, Praefixbeziehungen, Aligngrenzen und die 16 vollstaendigen
Replikplaene binden. Alle 14 Rollen muessen pro Ereignisposition dieselbe
oeffentliche Geschichte sehen. Keine Implementierung, kein Test, keine
Matrixzelle, kein Comparator und kein Forschungslauf.
