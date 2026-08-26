# S1AQ: C_i-Dreiarm-Replikation im Reiz-Gap-Reiz-Lauf

## Status

Technische Replikation des S1AP-Abgleichs mit drei getrennten Armen. Kein
Memory-, Lern-, Vergessens- oder Organismusnachweis.

## Arme

```text
P0     unveraenderter Feldzustand
leaky  lokale Austauschspur ohne C_i-Begrenzungsfaktor
C_i    begrenzte Akkommodationsbaseline mit (1-C_i^2)
```

Alle Arme erhielten dieselbe kontrollierte Weltfolge und denselben finalen
`probe.0`-Eingang. Verwendet wurden `alpha=0.5`, `dt=0.1`, `beta=0.25`.

## Ergebnisse am gemeinsamen Probe

```text
Arm       same Digest     changed Digest  History-Linf
P0        865a75b9a0c3    c513291418d3    0.018591847304592735
leaky     dbee4a890869    4b8f53c32b91    0.018569130534797640
C_i       ec32e4e0675b    f12b44bce000    0.018411941995273323
```

Abstand des jeweiligen gekoppelten Arms zu P0 im Probe:

```text
                 same                 changed
leaky            0.000280226653799398 0.000290562772438607
C_i              0.002690631309799657 0.002786769987944693
```

Maximale interne Zustandsbeträge ueber alle Phasen:

```text
                 same       changed
leaky            0.003050325 0.002867704
C_i              0.028337045 0.027445317
```

History-Abstand der internen Zustaende am Probe:

```text
leaky            0.001059999538728389
C_i              0.010146198428510209
```

## Einordnung

C_i erzeugt in dieser technischen Parametrisierung eine deutlich staerkere
interne Zustandsspanne und eine groessere Abweichung vom P0-Probe als der
leaky-Arm. Die History-Trennung der finalen Feldaktivierung ist jedoch nicht
C_i-spezifisch: P0, leaky und C_i zeigen dort fast denselben Abstand.

Der Lauf rechtfertigt deshalb keine Bezeichnung als Memory. Er zeigt nur,
dass die gewaehlte C_i-Projektion technisch staerker in den Feldzustand
eingreift als die gewaehlte leaky-Kontrolle. Offen bleibt, ob dieser Effekt
eine eigenstaendige Substratrolle hat oder nur eine staerkere
Rueckkopplungsamplitude ist.

## Naechster Schritt

Der naechste Schritt ist eine Amplituden-kontrollierte Nullhypothese: C_i und
leaky werden so kalibriert, dass ihre Probe-Abweichung von P0 gleich gross
ist. Danach wird nur noch geprueft, ob C_i bei gleicher Eingriffsamplitude
eine andere History-/Gap-Signatur liefert. Ohne diesen Ausgleich waere der
aktuelle Unterschied durch die groessere Rueckwirkungsamplitude erklaerbar.
