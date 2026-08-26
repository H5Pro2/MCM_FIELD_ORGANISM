# S1-CV: E1 Cue-Amplitudenrunner und Kurvenkern

## Status

Der amplitudenparametrische Einzelrunner, der interpretationsfreie
72-Beobachtungscontainer und die komponentenweise Linearitaetsmetrik sind
implementiert. Einzelne reale Arme und synthetische Kurven wurden geprueft;
eine reale 72er-Matrix oder Forschungsentscheidung wurde nicht erzeugt.

## Implementierung

```text
mcm_field_organism/e1_cue_amplitude_curve_execution.py
tests/test_e1_cue_amplitude_curve_execution.py
```

Alle Rollen bleiben privat.

## Einzelrunner

Der Runner akzeptiert genau ein Modell, eine Geschichte, eine Seite und eine
der vier registrierten Amplituden. E1 nutzt den eingefrorenen G4-Zustand,
B1 den einen statischen H8-Adapter und P0 keinen langsamen Adapter. n=2 und
n=4 beginnen jeweils auf frischen Feldkopien; der langsame Zustand wird
nicht fortgeschrieben.

Der kleinste isolierte E1-Arm `left-g4 / left / q=0.125` ist messbar:

```text
S/H L-inf:                    0.00032601928838195404
relativer n=2/n=4-Rest:       7.023618141288273e-13
```

P0 bleibt exakt null und B1 bei identischem Cue ueber die Geschichten
wertgleich. Diese Einzelwerte sind noch keine Amplitudenkurve.

## Kurvenkern

Der Kompositor akzeptiert exakt:

```text
3 Modelle * 3 Geschichten * 2 Seiten * 4 Amplituden = 72 Beobachtungen
```

Fuer jede Amplitude wird die gespiegelte passende-minus-gekreuzte
Historyinteraktion gebildet. Der q=1-Vektor ist die interne Referenz. Fuer
jede kleinere Amplitude wird komponentenweise der Rest gegen `q * I(1)`
berechnet.

Der Ergebniscontainer traegt rohe Beobachtungen, Interaktionsnormen,
lineare Residuen, P0/B1-Boeden, Spiegelungsfehler, Verfeinerungsrest und
S1-CT-Ankerfehler. Er besitzt kein Entscheidungs-, Rekonstruktions- oder
Memoryfeld.

## Synthetische Entscheidungsabnahme

Eine exakt lineare synthetische Kurve ergibt:

```text
AMPLITUDE_CURVE_EXPLAINED_BY_LINEAR_SCALING
```

Eine synthetische q=0.25-Abweichung oberhalb `0.05` ergibt:

```text
NONLINEAR_HISTORY_INTERACTION_RESIDUAL
```

Ungueltige Kontrollen haben Vorrang. Diese synthetischen Entscheidungen
sind keine Projektbefunde.

## Technische Abnahme

14 fokussierte Tests und 84 relevante Verbundtests bestehen. Geprueft
wurden kleinster Cue-Arm, P0, B1, n=2/n=4, Matrixvollstaendigkeit,
komponentenweise lineare Prognose, Entscheidungsreihenfolge und private API.

## Aussagegrenze

S1-CV bestaetigt nur, dass die vorregistrierte Amplitudenfrage technisch
ausfuehrbar und auswertbar ist. Es liegt noch kein realer Kurvenbefund vor.
Auch ein spaeterer nichtlinearer Rest waere nicht automatisch
Mustervervollstaendigung, Rekonstruktion oder Memory.

## Bester naechster Schritt

S1-CW bindet alle 72 Einzelrollen als lazy, schreibgeschuetztes Inventar mit
festem Digest. Beim Aufbau duerfen weder Einzelrunner noch Kompositor oder
Evaluator aufgerufen werden.
