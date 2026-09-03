# S2-KF - Einmalige uniforme PCM-Skalierung

## Status und Zweck

`S2KF_PROSPECTIVE_SINGLE_SCALE_CONTRACT_COMPLETE`

S2-KF ersetzt ausschliesslich die nicht materialisierbare
PCM-Amplitudenkonstruktion aus S2-KE. Der dortige Beleg und sein Status
`S2KC_AUDIO_GEOMETRY_NOT_MATERIALIZABLE` bleiben unveraendert erhalten.

Die neue Fixture-Version verwendet genau einmal den festen rationalen
Faktor:

```text
s = 24/25 = 0,96
```

Es gibt keine Suche, Normalisierung, Begrenzung, Wiederholung oder
nachtraegliche Anpassung.

## Koeffizientenbindung

Unveraendert gelten die Basen `U = 100 Hz` und `V = 8000 Hz`, jeweils mit
4.800 einzeln nach binary32 kanonisierten Samples. `mU` und `mV` werden wie
in S2-KD aus genau einer realen Rezeptorauswertung je Basis bestimmt.

Die binary64-Reihenfolge lautet:

```text
s64 = 24.0 / 25.0
c64 = (33.0 / 2000.0) * s64
h64 = ( 1.0 /  100.0) * s64
b64 = ( 1.0 /  200.0) * s64

alpha_U  = f32(c64 / mU)
alpha_HV = f32(h64 / mV)
alpha_BV = f32(b64 / mV)

alpha_PLUS_V  = f32(alpha_HV + alpha_BV)
alpha_MINUS_V = f32(alpha_HV - alpha_BV)
```

Damit sind die prospektiven Rezeptorbeitraege:

```text
c' = 0,01584
h' = 0,00960
b' = 0,00480
```

Samplebildung und Rundungsreihenfolge bleiben exakt S2-KD. Jeder Wert muss
vor einer Rezeptor- oder Memoryannahme endlich und in `[-1,1]` liegen.

## Vorab gebundenes reales Startgate

Nach bestandener Samplegrenze werden die tatsaechlichen 48-Werte-Zustaende
einmal gemessen. Nur folgende Intervalle sind zulaessig:

```text
0,02010 <= d(H_AUDIO,T_PLUS)  <= 0,02120
0,02010 <= d(H_AUDIO,T_MINUS) <= 0,02120
0,00900 <= d(T_PLUS,T_MINUS)  <= 0,01020
d(H_AUDIO,P6) <= 0,01850

0,02900 <= d(N_AUDIO,T_PLUS) <= 0,03150
0,02010 <= d(N_AUDIO,T_MINUS) <= 0,02120
d(N_AUDIO,P6) >= 0,02700
```

Zusaetzlich muessen alle sechs adaptiven Vorabstaende hoechstens `0,02`
betragen, alle D1-D9-Distanzen ausserhalb der unveraenderten auditiven
Schwelle liegen und die vier zentralen Rollen denselben visuellen
Rezeptorzustand besitzen.

Diese Intervalle sind vor der neuen Auswertung festgelegt. Die analytischen
Zielwerte `0,02064`, `0,00960` und ungefaehr `0,01810` ersetzen keine reale
Messung.

## Unveraenderte Grenzen

- auditive Schwelle `0,02`, PPB-Update `0,05` und Supportgrenze `3`;
- Formation, Checkpoints, Holdouts und drei unabhaengige Baselines;
- Umfang `17/8/157`;
- keine Aenderung an Rezeptor, B4, TSPM-1, PPB-1, Kontext oder Feld;
- keine Rohdaten in Memory- oder Ergebnisbelegen;
- `memory_calls = 0`, solange das gesamte Startgate nicht besteht.

Verletzt die neue Fixture Samplegrenze oder Messintervalle, endet S2-KF als
`S2KF_AUDIO_GEOMETRY_NOT_MATERIALIZABLE`. Diese auditive Konstruktion wird
dann geschlossen; ein weiterer Parametersuchzyklus ist nicht zugelassen.
