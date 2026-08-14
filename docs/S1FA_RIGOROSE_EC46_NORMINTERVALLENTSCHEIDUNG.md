# S1-FA: Rigorose EC46-Normintervallentscheidung

## Forschungsfrage

Kann der vorregistrierte EC46-Ausgang trotz fehlender r2/r4/r8-
Differenzvektoren durch mathematisch sichere Grenzen eingeordnet werden,
ohne Vektoren zu rekonstruieren oder einen Lauf zu wiederholen?

## Methode

Fuer jede Norm gilt die umgekehrte Dreiecksungleichung:

```text
| ||v|| - ||w|| | <= ||v - w|| <= ||v|| + ||w||
```

Die gespeicherten L-infinity-Normen bestimmen daher gueltige Intervalle fuer
die unbekannten Grob- und Feinabstaende. Sie bestimmen nicht die exakten
Abstaende.

## Ergebnis

| Komponente | minimaler r4/r8-Rest | Minimum relativ zu r8 | EC46-Grenze |
|---|---:|---:|---:|
| Aktivierung | `1.161414602268707e-07` | `0.09761594566271163` | `0.01` |
| Nachhall | `6.86837006436125e-08` | `0.09548275400641616` | `0.01` |

Schon der jeweils kleinstmoegliche Feinrest liegt bei rund 9,6 bis 9,8 % des
r8-Signals. Damit kann die vorregistrierte relative 1%-Konvergenz fuer keine
mit den gespeicherten Normen vereinbare Vektorrichtung bestehen.

Die Nullkontrollen sind bekanntlich null und beide r8-Signale liegen ueber
`1e-12`. Der klare EC46-Ausgang ist mathematisch ausgeschlossen. Der dadurch
eindeutige technische EC46-Ausgang lautet:

`NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE`.

## Einordnung

EC97 bleibt hinsichtlich der Datenluecke richtig: Exakte Grob- und
Feinabstaende sind nicht berechenbar. S1-FA rekonstruiert keine Vektoren,
sondern zeigt, dass fuer die Entscheidungsgrenze bereits eine sichere
Untergrenze ausreicht.

Der gemessene zustandsabhaengige Effekt und seine Nullablationen bleiben ein
technischer Befund. Die vorhandene Verfeinerungsfolge erfuellt jedoch den
vorregistrierten Konvergenzvertrag nicht. Das ist kein Memory-, Feldzeit-,
Organisations-, Topologie-, Semantik-, Selbstregulations- oder KI-Nachweis.

## Bester naechster Schritt

Am besten geht es mit S1-FB weiter: statisch untersuchen, ob der beobachtete
Rueckgang ueber r2/r4/r8 aus der gebundenen Diskretisierungs- und
Schrittskalierung des Runners folgt oder auf fehlende numerische Stabilitaet
hinweist. Keine Wiederholung und keine nachtraegliche Aenderung von EC46.
