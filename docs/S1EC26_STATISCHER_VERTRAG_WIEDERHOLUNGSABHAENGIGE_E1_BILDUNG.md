# S1-EC26: Statischer Vertrag fuer wiederholungsabhaengige E1-Bildung

## Status

```text
CANONICAL_AV_EPISODE_BOUND
ONE_TWO_FOUR_EIGHT_CONTACT_SCHEDULES_BOUND
CONTINUOUS_CONTROLS_EXPOSURE_MATCHED
BASELINES_AND_DECISIONS_PREREGISTERED
PLANNER_IMPLEMENTATION_ONLY
NO_FIELD_EXECUTION
NO_IMPRINTING_MEMORY_OR_AI_CLAIM
```

S1-EC26 bindet die in EC25 ausgewaehlte Wiederholungsbildungsfrage an die
vorhandene kontrollierte AV-Quelle. Es wird kein Feld ausgefuehrt und noch
kein neuer Planner implementiert.

## Kanonische Episode

```text
input bundle digest = 33f2d8479a37a3697374b3f10dd4581ac41684bb3d75e86fabf33568ef77e60f
episode contact digest = ef9e3b9c7f95320891c6900832d6f0796029efddad90f2a7e9e13fdced1f084c
episode supports = 110
episode duration = 1,000,000 ticks
signed integral = 6.941865469153374
absolute integral = 6.941865469153374
quadratic integral = 1.512406472248469
```

Die Episode ist bereits durch die EC4/EC5-Planstruktur r2/r4/r8 gebunden.
Sie wird fuer die Forschungsarme wertidentisch wiederverwendet; Labels oder
Inhaltsklassen werden nicht eingefuehrt.

## Kontaktplaene

Alle Arme enden bei `15.000.000` Ticks. Eine Episode dauert `1.000.000`
Ticks, die feste neutrale Trennung ebenfalls `1.000.000` Ticks. Innerhalb
jedes Paars endet auch der letzte Kontakt am selben Tick. Dadurch wird keine
zusaetzliche kontaktfreie Abschwaechungszeit mit Wiederholung vermischt.

| Anzahl | getrennte Startticks | kontinuierlicher Kontakt | Kontaktzeit je Paar | Supports je Paararm |
|---:|---|---|---:|---:|
| 1 | `0` | `0..1.000.000` | 1.000.000 | 110 |
| 2 | `0, 2.000.000` | `1.000.000..3.000.000` | 2.000.000 | 220 |
| 4 | `0, 2.000.000, 4.000.000, 6.000.000` | `3.000.000..7.000.000` | 4.000.000 | 440 |
| 8 | `0, 2.000.000, ..., 14.000.000` | `7.000.000..15.000.000` | 8.000.000 | 880 |

Je Anzahl sind Episode, Supportwerte, Gesamtenergie, Kontaktzeit,
Gesamthorizont und letzter Kontaktabschluss gleich. Nur die zeitliche
Gliederung unterscheidet sich. Der Ein-Kontaktarm ist eine zwingende
Identitaetskontrolle.

## Pflichtkontrollen

- P0 und E1-Bildungsablation;
- dauer-, energie- und horizontangepasste leaky-, F3- und CONST-V-Baselines;
- identische spaetere Probe auf frischen gleichen Feldern;
- Zustandsaustausch und Neutralisierung;
- fester Adapter nur als Uebertragungskontrolle;
- Observer aus, Snapshot/Restore invariant;
- r2/r4/r8 mit nichtzunehmendem feinen Rest;
- keine nachtraegliche Schwellen-, Parameter- oder Armveraenderung.

## Vorregistrierte Entscheidung

```text
Pflichtgate oder Baseline fehlerhaft
-> TECHNICALLY_INVALID

alle n2/n4/n8-Zustands- und Probenkontraste bitgenau null
-> NO_REPETITION_DEPENDENT_FORMATION

alle n2/n4/n8-Zustands- und Probenkontraste strikt groesser als
8 * passender feiner Rest und nicht gleichwertig durch Pflichtbaseline erklaert
-> REPETITION_DEPENDENT_FORMATION_CANDIDATE

sonst
-> NUMERICALLY_UNDECIDABLE
```

Ein positiver Ausgang waere nur ein Kandidat fuer wiederholungsabhaengige
Bildung. Er waere noch kein Nachweis fuer Praegung, Vergessen, Memory,
Feldzeit, Organisation oder KI.

## Bester naechster Schritt

S1-EC27 sollte ausschliesslich den Schedule- und Quellenplanner
implementieren und synthetisch pruefen: Supportreplay, Gap-Nullbereiche,
kontinuierliche Vergleichsarme, Integrale, Horizon und r2/r4/r8-Handoff.
Noch kein E1-Feldlauf und keine Ergebnisentscheidung.
