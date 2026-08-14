# S1-CU: E1 Cue-Amplitudenkurvenvertrag

## Status

Die naechste Pruefung der history-spezifischen Hinweiswirkung ist statisch
vorregistriert. S1-CU hat keinen Cue ausgefuehrt, keine 72er-Matrix erzeugt
und keine Entscheidung abgeleitet.

```text
Vertragsdigest: 88e56327c18c2c39244befff17747e99dbf0110e68a5ecb99c32cb63c625cbe0
```

## Forschungsfrage

Wird die in S1-CT beobachtete Historyinteraktion ueber mehrere
Hinweisstaerken vollstaendig durch lineare Amplitudenskalierung erklaert,
oder verbleibt nach Kontrolle von P0, statischem B1, Spiegelung und Numerik
ein reproduzierbarer nichtlinearer Rest?

## Amplituden und Rollen

```text
Amplituden:   0.125, 0.25, 0.5, 1.0
Modelle:      E1, P0, B1-static-H8
Geschichten:  left-g4, right-g4, neutral
Seiten:       left, right

3 * 3 * 2 * 4 = 72 spaetere Beobachtungen
```

Linke und rechte Hinweise sind bei jeder Staerke gespiegelt und
energiegleich. Geschichte, G4-Abstand, Hinweisdauer und 20-Hz-Zeitplan
bleiben gegenueber S1-CT unveraendert.

## Primaere Nullprognose

```text
Interaktion(q) = q * Interaktion(1.0)
```

Die Prognose gilt komponentenweise fuer den vollstaendigen signierten S/H-
Interaktionsvektor, nicht nur fuer dessen L-inf-Norm. Der Vollkontaktanker
ist an den unveraenderten S1-CT-Bericht gebunden:

```text
S1-CT Bericht SHA-256: ee569666e63ab7f4821f5778c3fb80d62a02f47bf3269c871b8e05bf1a450d26
S1-CT Vollinteraktion:  0.0021516247701185154
```

## Metriken

- Interaktions-L-inf je Amplitude;
- komponentenweiser Rest gegen `q * I(1)`;
- maximaler relativer linearer Rest;
- P0- und B1-Interaktionsboden;
- Spiegelungsfehler und n=2/n=4-Rest;
- Abweichung des neuen q=1-Arms vom S1-CT-Anker.

Die absolute Kontrolltoleranz bleibt `1e-12`, die relative
Verfeinerungsgrenze `0.01` und die vorregistrierte relative
Linearitaetsgrenze `0.05`.

## Entscheidungsreihenfolge

```text
INVALID_S1_CU_RUN
NO_MEASURABLE_HISTORY_INTERACTION
AMPLITUDE_CURVE_EXPLAINED_BY_LINEAR_SCALING
NONLINEAR_HISTORY_INTERACTION_RESIDUAL
```

Auch ein nichtlinearer Rest waere nur ein technischer Differenzbefund. Er
darf nicht automatisch als Mustervervollstaendigung, Rekonstruktion oder
Memory interpretiert werden.

## Technische Abnahme

Sieben fokussierte Vertragstests und 77 relevante Verbundtests bestehen.
Geprueft wurden Rollenanzahl, Cue-Spiegelung, Energiegleichheit,
S1-CT-Anker, feste Nullprognose, Digest, Aenderungssperren und private API.

## Bester naechster Schritt

S1-CV implementiert einen amplitudenparametrischen Einzelrunner sowie den
interpretationsfreien 72-Beobachtungscontainer und die komponentenweise
Linearitaetsmetrik. Zunaechst werden nur einzelne Arme und synthetische
Kurven getestet; eine Gesamtmatrix bleibt gesperrt.
