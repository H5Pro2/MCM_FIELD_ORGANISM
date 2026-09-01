# S2-JC Befund

Status:

`S2JB_RECEPTOR_AGGREGATE_EQUIVALENCE_QUALIFIED`

Die zwei fehlerhaften S2-JB-Fixturepfade wurden eng korrigiert. Jeder
`VisualReceptorState` wird nun genau einmal im gemeinsamen Hilfsweg in einen
`ReceptorContactFrame` umgewandelt. Das Produktmodul und die uebrigen 48
Testkoerper blieben unveraendert.

Der statische Vorabcheck bestaetigte:

- genau 50 aktive Tests;
- genau eine aktive Umwandlungsstelle;
- unveraenderten Produktmodulhash;
- keine Memory-, Kontext- oder Hauptausfuehrung ausserhalb der gebundenen
  Qualifikation.

Der einzige S2-JC-`unittest`-Aufruf bestand mit:

```text
Ran 50 tests in 0.928s
OK
Exit-Code 0
```

Die Suite erreichte die gebundenen Zaehler:

```text
Quellmaterialisierungen              286
Aggregatcodebildungen                 286
PPB-Formationsschritte                214
Aggregatcodevergleiche                 50
diagnostische Baselinevergleiche      126
validierte PPB-Linienschritte         230
maximale logische Arbeitspositionen  1192
```

Damit ist qualifiziert:

- gleiche Aggregatsummen bleiben trotz verschiedener Rohframes aequivalent;
- direkt benachbarte Summen bleiben verschieden;
- homogene PPB-Formationsketten werden akzeptiert;
- gemischte, unvollstaendige, vertauschte oder fremde Ketten stoppen
  fail-closed;
- exakte Floatgleichheit sowie beide L1-Regeln bleiben diagnostische
  Gegenbaselines.

Es gab keinen Retry. Produkt- und Testquellhashes blieben waehrend des Laufs
unveraendert. S2-IV bleibt dauerhaft falsifiziert.

S2-JC qualifiziert die private Aggregatecode-Aequivalenz. Eine Integration
in den privaten Kontextsignalgeber ist noch nicht Bestandteil dieses Laufs.
