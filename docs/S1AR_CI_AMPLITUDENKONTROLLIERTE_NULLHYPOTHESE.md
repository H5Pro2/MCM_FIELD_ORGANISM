# S1AR: Amplitudenkontrollierte C_i-Nullhypothese

## Status

Technischer Kontrolllauf zur Trennung von Rueckwirkungsamplitude und
Substratmechanik. Kein Memory-, Lern- oder Organismusnachweis.

## Aufbau

Die C_i-Baseline wurde unveraendert mit `alpha=0.5`, `beta=0.25` und
`dt=0.1` gefuehrt. Der leaky-Arm blieb in seiner Zustandsentwicklung
unbegrenzt, erhielt aber `beta=2.4`, damit seine Probe-Abweichung von P0
ungefaehr der C_i-Abweichung entspricht.

Beide Arme erhielten dieselbe Folge:

```text
contact.0 -> gap.0 -> contact.1 -> probe.0
```

## Ergebnisse

```text
Arm       Abstand zu P0 same       Abstand zu P0 changed   History-Linf am Probe
C_i       0.002690631309799657     0.002786769987944693     0.018411941995273323
leaky     0.002690175876474160     0.002789402615410497     0.018373766314560003
```

Die direkte Differenz zwischen den beiden gekoppelten Armen am Probe betrug:

```text
same     Linf 0.000221295401827012
changed  Linf 0.000133787901120105
```

Die internen Zustandsdifferenzen zwischen den beiden Vorgeschichten blieben
unterschiedlich:

```text
C_i      Linf 0.010146198428510209
leaky    Linf 0.001059999538728389
```

## Einordnung

Nach Angleichung der Probe-Abweichung zu P0 ist die History-Trennung der
Feldaktivierung bei C_i und leaky praktisch gleich. Der vorherige groessere
C_i-Effekt auf den Probe kann damit weitgehend durch seine groessere
Rueckwirkungsamplitude erklaert werden.

C_i traegt weiterhin einen staerkeren internen Zustand weiter als leaky. Das
allein unterscheidet C_i aber noch nicht von einer staerkeren technischen
Spur. Es gibt deshalb weiterhin keinen zulaessigen Memoryclaim.

## Entscheidung fuer die weitere Linie

Die aktuelle Minimalgleichung ist als Engineering-Baseline ausreichend
charakterisiert. Eine weitere reine Parametersteigerung waere nicht
informativ. Der naechste sinnvolle Schritt ist ein kontrollierter
Abschwaechungs- und Freigabetest: Nach identischem Kontakt wird nur die
Abklingdynamik ueber mehrere Gap-Laengen verglichen, mit P0 und amplituden-
kalibriertem leaky als Kontrollen. Geprueft wird nur die Form der technischen
Abschwaechung, nicht Vergessen als geistige oder organische Eigenschaft.
