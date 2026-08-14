# S1-DS: E1 verfeinerter Weltkontakt-Bildungsvertrag

## Forschungsfrage

Kann derselbe kontrollierte audiovisuelle Weltinhalt allein durch die
Reihenfolge AB gegen BA aus einem frischen neutralen E1-Zustand
unterschiedliche lokale Zustaende bilden, deren spaetere Feldwirkung auch
nach einer unabhaengigen Zeitverfeinerung bestehen bleibt?

S1-DS beantwortet diese Frage noch nicht. Es bindet nur den neuen
experimentellen Vertrag vor Implementierung und Ausfuehrung.

## Abgrenzung zum gestoppten Zweig

S1-DI und S1-DQ werden nicht wiederholt. Ihre Ergebnisdateien bleiben
unveraendert und ihre Einmallaufpfade verbraucht. S1-DS verwendet nur die
kontrollierte AV-Quelldefinition und den in S1-DR festgestellten offenen
Forschungsbedarf. Es uebernimmt keine alte Zustandsdifferenz als Ergebnis.

Der neue Korridor beginnt spaeter mit frischen Feldern und frischen neutralen
E1-Zustaenden. Der volle alte S1-DC-Befund bleibt gestoppt.

## Statische Bindung

```text
mcm_field_organism/e1_refined_world_formation_contract.py
tests/test_e1_refined_world_formation_contract.py
```

Vertragsdigest:

```text
de996ac492af3808499b222687ac92d6f2110eda34743cc65d623ee3d924cbd7
```

Gebunden sind:

- der S1-DR-Klassifikationsdigest;
- die kontrollierten AB-/BA-Quellen- und Permutationsdigests;
- die direkt aus dem ersten A-Block neu berechnete identische Probe;
- 200 auditive und 20 visuelle History-Frames mit 220 eindeutigen Supports;
- zwei Sekunden physische History-Zeit mit Blockgrenze bei einer Sekunde;
- 84 Feldknoten und 145 lokale E1-Kanten;
- drei feste Verfeinerungen `r1`, `r2` und `r4`.

## Verfeinerungsmethode

Jedes durch Rezeptorabschluesse begrenzte physische Integrationsintervall
wird in 1, 2 oder 4 gleich lange Teilschritte zerlegt. Horizont,
Rezeptorabschluesse, Supportinventar und das ueber das Intervall integrierte
lokale Eingangssignal muessen dabei identisch bleiben.

Damit veraendert die Verfeinerung nur die numerische Zeitaufloesung der E1-
und S/H-Entwicklung, nicht die audiovisuelle Testwelt.

## Pflichtarme

Je Verfeinerung werden getrennt gebunden:

- AB-Bildung und BA-Bildung mit entwickelbarem E1, aber ablatierter
  E1-Rueckwirkung auf das History-Feld;
- eine unabhaengige AB-Identitaetswiederholung;
- eine Bildungsablation, bei der E1 neutral bleiben muss;
- frische identische Probefelder fuer P0, aktive gebildete Zustaende,
  Probeablation und passende feste Adapter.

Die gebildeten E1-Zustaende bleiben waehrend der spaeteren Probe
eingefroren.

## Metriken und Kontrollen

Zustandsabstand wird als Linf-Abstand der geordneten 145 Kantenbindungen
gemessen. Die Probe verwendet geordnete S/H-Linf-Abstaende. Getrennt
berichtet werden unter anderem Zustands- und Probensignal, grober und feiner
Verfeinerungsrest, Identitaetsrest, Bildungs- und Probeablation,
Fixed-Adapter-Rest sowie Ressourcenbilanzfehler.

Elf Kontrollen binden Frische, Quellenidentitaet, Zeithorizont,
Supportvollstaendigkeit, Identitaetswiederholung, neutrale Bildungsablation,
frische Probefelder, eingefrorene Zustaende, P0-Ablation, Fixed-Adapter-
Gleichheit und unveraenderte oeffentliche API.

## Vorregistrierte Entscheidung

Die Regeln werden in dieser Reihenfolge angewendet:

1. Fehler einer Pflichtkontrolle: `TECHNICALLY_INVALID`.
2. Alle Zustands- und Probensignale in `r1/r2/r4` bitgenau null:
   `NO_REFINED_WORLD_FORMATION_EFFECT`.
3. Feiner Zustands- sowie beide feinen Probeneffekte liegen jeweils ueber
   dem Achtfachen ihres passenden feinen Restes, und jeder feine Rest ist
   nicht groesser als sein grober Rest:
   `REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT`.
4. Jeder andere Ausgang: `NUMERICALLY_UNDECIDABLE`.

Der Faktor acht ist vor jeder Ausfuehrung gebunden. Nachparametrierung ist
nicht zulaessig.

## Freigabegrenze

S1-DS erlaubt nur die naechste Implementierung. Nicht erlaubt sind:

- eine Ausfuehrung des neuen Korridors;
- Wiederholungen von S1-DI oder S1-DQ;
- Memory-, Semantik-, Organisations-, Topologie-, Selbstregulations- oder
  KI-Claims.

## Technische Abnahme

```text
6 fokussierte Vertragstests
321 Tests im vollstaendigen E1-Verbund
OK
```

## Bester naechster Schritt

S1-DT implementiert ausschliesslich den completion-aligned
Verfeinerungsplaner und prueft ihn mit kleinen synthetischen Intervallen.
Er muss fuer `r1/r2/r4` exakt denselben Horizont und dasselbe integrierte
lokale Eingangssignal nachweisen. Die kanonischen AB-/BA-Historien und die
Probe bleiben dabei unaufgerufen.

## Anschlussstatus nach S1-DT

S1-DT hat den privaten Planer inzwischen synthetisch implementiert und
abgenommen. Kanonische AB-/BA-Historien und Probe blieben unaufgerufen. Der
aktuelle Anschluss steht in
`S1DT_E1_COMPLETION_ALIGNED_VERFEINERUNGSPLANER.md`.
