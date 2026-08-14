# S1-EB1: E1 completion-aligned R8-Planer

## Status

Der private, geometrieneutrale `r2/r4/r8`-Planer ist implementiert und nur
mit einer kleinen synthetischen Rezeptorsequenz abgenommen. Es wurden keine
kanonischen AB-/BA- oder Probepfade geplant und keine Feldruntime aufgerufen.

## Implementierung

```text
mcm_field_organism/e1_confirmation_refinement_planner.py
tests/test_e1_confirmation_refinement_planner.py
```

Normalisierter Implementierungsdigest:

```text
cf50c5757e420a6ad8c84b248b41ccf2028c90c7a1116a8f4e3b377453215731
```

## Trennung von S1-DT

Der bestehende S1-DT-Planer bleibt unveraendert und weiterhin fest an
`r1/r2/r4` gebunden. S1-EB1 verwendet eigene Plan- und Planmengencontainer,
die den S1-EB-Vertragsdigest verlangen. Dadurch werden keine historischen
Implementierungs- oder Vertragsdigests nachtraeglich veraendert.

## Planregel

Fuer jede vorhandene Abschlussgrenze wird das davorliegende Intervall exakt
durch Faktor `2`, `4` oder `8` geteilt. Der Rezeptorkontakt bleibt
punktfoermig am gemessenen Abschluss des Intervalls. Ein Intervall, das nicht
ohne Rest durch acht teilbar ist, wird abgewiesen.

Jeder Plan bindet:

- denselben physischen Horizont;
- dieselben Abschlusszeiten;
- denselben Quellkontaktdigest;
- dieselbe Zahl und Exactly-once-Zuordnung der Supports;
- exakt dasselbe signierte Kontaktintegral;
- exakt dasselbe absolute Kontaktintegral;
- exakt dasselbe quadratische Kontaktintegral;
- einen eigenen schrittweitenabhaengigen Plandigest.

## Synthetische Abnahme

Zwei Abschlussintervalle erzeugten:

```text
r2 = 4 Schritte
r4 = 8 Schritte
r8 = 16 Schritte
```

Beide Supports blieben an Tick `8` und `16`. Die Kontaktintegrale blieben
exakt:

```text
signiert    = -0.25
absolut     = 0.75
quadratisch = 0.3125
```

## Technische Abnahme

```text
7 fokussierte Tests
424 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

S1-EB1 ist nur Numerikplanung. Es liefert keinen kanonischen
Bestaetigungswert und keinen Memory-, Semantik-, Organisations-, Topologie-,
Selbstregulations- oder KI-Befund.

## Anschluss

S1-EB2 hat den nichtausfuehrenden kanonischen Preflight abgeschlossen. AB,
BA und die identische 110-Support-Probe sind mit `r2/r4/r8` gebunden; Feld,
E1 und Einmallaufpfade blieben unberuehrt. Siehe
[S1-EB2 kanonischer r2/r4/r8-Preflight](S1EB2_E1_KANONISCHER_R2_R4_R8_PREFLIGHT.md).
