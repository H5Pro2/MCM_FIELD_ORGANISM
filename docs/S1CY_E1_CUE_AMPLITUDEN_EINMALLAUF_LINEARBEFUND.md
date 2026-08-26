# S1-CY: E1 Cue-Amplituden-Einmallauf und Linearbefund

## Status

Die in S1-CX registrierte 72er-Amplitudenkurve wurde genau einmal
ausgefuehrt und atomar gespeichert. Alle Beobachtungen und Kontrollen sind
vollstaendig. Die vorhandene Ergebnisdatei sperrt eine Wiederholung.

## Technische Entscheidung

```text
AMPLITUDE_CURVE_EXPLAINED_BY_LINEAR_SCALING
```

## Kurvenwerte

```text
q=0.125  Interaktion L-inf = 0.0002689530962648144
q=0.25   Interaktion L-inf = 0.0005379061925296288
q=0.5    Interaktion L-inf = 0.0010758123850592577
q=1.0    Interaktion L-inf = 0.0021516247701185154
```

Komponentenweise gilt fuer jede Amplitude exakt:

```text
I(q) = q * I(1.0)
```

Alle vier linearen Residuen sind `0.0`; der maximale relative lineare Rest
ist ebenfalls `0.0`.

## Kontrollen

```text
P0-Interaktionsboden:       0.0
B1-Interaktionsboden:       0.0
Spiegelungsfehler L-inf:    1.3877787807814457e-17
relativer n=2/n=4-Rest:     2.5868378748081485e-12
S1-CT-Ankerfehler L-inf:    0.0
Kontrollen:                 bestanden
```

## Ergebnisartefakt

```text
reports/e1_cue_amplitude_s1cy_once_v1.json
Bericht SHA-256:  17b10cf41b9cc53245dd66392b1c518f77ed983614d235e69c903e85f2ce3f43
Ergebnis SHA-256: c5b867caf489b137edcdebf5753ab86fbd0f1d4ea1ec56e58c0bf1137c13734c
Vertrag SHA-256:  ac9ff73915423bde98f9f25e93c540e0345ae236d1d1430f9d9fef0dd81b177f
```

Vor dem realen Start bestanden 11 fokussierte Einmallauftests und 102
relevante Verbundtests. Alte Einmallaufe wurden nicht wiederholt.

## Wissenschaftliche Einordnung

S1-CT bleibt gueltig: Der E1-Zustand vermittelt eine kontrollierte,
history-spezifische spaetere Feldwirkung, die P0 und ein einzelner statischer
H8-Adapter nicht erzeugen.

S1-CY zeigt zugleich, dass der Teilhinweis diese Wirkung lediglich linear
skaliert. Es gibt in diesem Korridor keine nichtlineare
Mustervervollstaendigung und keinen Hinweis darauf, dass ein schwacher Cue
eine vollstaendigere fruehere Feldlage rekonstruiert.

## STOPP: Rekonstruktionszweig

Weitere Amplitudenpunkte, Cue-Unterteilungen oder Wiederholungen derselben
eingefrorenen E1-Probe waeren nur weiteres Gleichungs-Engineering entlang
einer bereits exakt bestaetigten linearen Wirkung. Dieser Zweig darf nicht
als Rekonstruktions- oder Memorysuche fortgesetzt werden.

Das Gesamtprojekt ist nicht gestoppt. Vor einem neuen Lauf muss jedoch
konzeptionell geprueft werden, ob eine funktionale Umpraegungs- und
Wiedererwerbspruefung gegen die bereits vorhandenen E3/E4-Befunde neue
Evidenz liefern kann oder nur die programmierte E1-Freigabe wiederholt.

## Bester naechster Schritt

S1-CZ ist zunaechst ein statischer Richtungs- und Evidenzaudit ohne
Implementierung. Er vergleicht S1-CD, S1-CN, S1-CT und S1-CY und bestimmt,
welches noch unbelegte Memory-Mindestkriterium mit E1 ueberhaupt fair
pruefbar ist. Erst wenn eine neue Gegenprognose gegen die bekannte lineare
Adapter- und Freigabewirkung existiert, darf ein weiterer Lauf registriert
werden.
