# S1AP: C_i-Reiz-Gap-Reiz-Abgleich

## Status

Technischer Abgleich der gekoppelten C_i-Baseline in der kontrollierten
synthetischen Audio-/Video-Holdout-Welt. Der Lauf belegt kein Memory, Lernen,
Vergessen oder Organismusverhalten.

## Forschungsfrage

Bleibt nach `contact.0 -> gap.0 -> contact.1 -> probe.0` ein lokaler C_i-Zustand
erhalten, der den identischen Probe-Eingang zwischen zwei Vorgeschichten
unterscheidbar macht?

## Aufbau

- Weltfamilie: `controlled_history_holdout_world_family()`;
- `history.same` wiederholt den ersten Kontakt;
- `history.changed` verwendet einen veraenderten zweiten Kontakt;
- beide erhalten danach denselben `probe.0`;
- C_i: `alpha=0.5`, `dt=0.1`, `beta=0.25`;
- Referenz: unveraenderter P0-Feldzustand;
- keine Kamera, kein Mikrofon, keine externe Quelle.

## Ergebnis

```text
Messgroesse                                      Ergebnis
C_i-Zustandsdifferenz am gemeinsamen Probe       Linf 0.010146198428510209
P0-Aktivierungsdifferenz am gemeinsamen Probe     Linf 0.018591847304592735
C_i-gekoppelte Aktivierungsdifferenz              Linf 0.018411941995273323
C_i-gekoppelte Aktivierungsdifferenz              L1   0.5331798735882392
C_i vs P0 im same-Probe                           Linf 0.002690631309799657
C_i vs P0 im changed-Probe                        Linf 0.0027867699879446928
```

Die maximale C_i-Auslenkung je Phase war in `history.same`:

```text
contact.0  0.010580302
gap.0      0.013329670
contact.1  0.024297314
probe.0    0.028337045
```

und in `history.changed`:

```text
contact.0  0.010580302
gap.0      0.013329670
contact.1  0.019112959
probe.0    0.027445317
```

## Einordnung

C_i fuehrt einen lokalen Zustand durch die Kontakt-/Lueckenfolge weiter und
unterscheidet die beiden Vorgeschichten am gemeinsamen Probe. Der Effekt ist
jedoch nicht groesser als die bereits vorhandene P0-Feldspur. Die gekoppelte
C_i-Projektion veraendert den Probe-Verlauf gegenueber P0 nur geringfuegig.

Damit ist die Bedingung "Zustand bleibt nach einer Luecke erhalten" technisch
erfuellt, die staerkere Bedingung "unabhaengiges Substrat statt gewoehnlicher
Feldspur" aber nicht. Ein Memoryclaim ist deshalb weiterhin unzulaessig.

## Naechster Schritt

Als kleinster besserer Schritt folgt eine identische Reiz-Gap-Reiz-Replikation
mit drei Armen: P0, leaky und C_i. Alle drei muessen denselben Probe-Eingang
erhalten; ausgewertet werden nur History-Trennung, Probe-Stabilitaet und die
Differenz zum jeweiligen Arm. Erst eine C_i-spezifische Abweichung gegen beide
Kontrollarme wuerde eine weitere Substratpruefung rechtfertigen.
