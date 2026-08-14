# S1-EC27: Quellen- und Schedule-Planner der Wiederholungsbildung

## Status

```text
ALL_EIGHT_REPEATED_CONTINUOUS_ARMS_PLANNED
SOURCE_PAYLOADS_VALUE_IDENTICAL
EXPOSURE_AND_FINAL_COMPLETION_MATCHED
R2_R4_R8_HANDOFFS_COMPLETE
ALL_SUPPORTS_ASSIGNED_ONCE
NO_E1_OR_FIELD_EXECUTION
NO_RESULT_DECISION_OR_CLAIM
```

S1-EC27 implementiert den in EC26 freigegebenen Planner. Er erzeugt aus der
kanonischen 110-Support-AV-Episode getrennte und kontinuierliche
`1/2/4/8`-Rezeptorsequenzen sowie deren completion-aligned r2/r4/r8-Plaene.
Kein E1-Zustand und kein MCM-Feld werden fortgeschrieben.

Die anschliessende reale EC28-Consumerabnahme deckte zusaetzlich auf, dass
die erste Plannerfassung zwar Organismuszeit und Snapshot-ID, aber nicht die
technische Quellzeit eines Replays verschob. Die Runtime stoppte den zweiten
Kontakt deshalb korrekt als doppelten Quellsupport. EC27 wurde vor einem
kanonischen Lauf korrigiert: Quell- und Organismusintervalle werden jetzt um
denselben Episodenoffset verschoben; Werte und Dauer bleiben unveraendert.

## Korrigierte Zeitkontrolle

Die erste synthetische Plannerabnahme zeigte eine unzulaessige
Konfundierung: Im urspruenglichen n8-Entwurf endete der kontinuierliche
Kontakt sieben Millionen Ticks vor dem getrennten Kontakt. Unterschiedliche
kontaktfreie Nachzeit haette dadurch Wiederholung mit Aktualitaet vermischt.

**STOPP wurde gesetzt und vor jeder Feldbildung korrigiert.** Der
kontinuierliche Block endet nun in jedem Paar exakt mit dem letzten
getrennten Kontakt:

| Anzahl | getrennte Kontakte | kontinuierlicher Block | gemeinsamer letzter Abschluss |
|---:|---|---|---:|
| 1 | Start `0` | `0..1.000.000` | 1.000.000 |
| 2 | Starts `0, 2.000.000` | `1.000.000..3.000.000` | 3.000.000 |
| 4 | Starts `0, 2.000.000, 4.000.000, 6.000.000` | `3.000.000..7.000.000` | 7.000.000 |
| 8 | Starts `0, 2.000.000, ..., 14.000.000` | `7.000.000..15.000.000` | 15.000.000 |

Damit sind Episode, Werte, Supports, Kontaktzeit, Integrale, Gesamthorizont
und letzter Kontaktabschluss paarweise gleich. Nur die zeitliche Gliederung
ist verschieden.

## Plannerergebnis

```text
corrected S1-EC26 contract digest = da09a338abbcd3501428ce90e28399da3269e4579bf8a08d65dcbda1e7026af5
S1-EC27 plan-set digest = b53d1e1c94dedaf4d7cd8aac250d8c81bd0ebc0b0e2ea69ecd7e0e3716b365ea

n1 supports = 110, r2/r4/r8 steps = 202/404/808
n2 supports = 220, r2/r4/r8 steps = 402/804/1608
n4 supports = 440, r2/r4/r8 steps = 802/1604/3208
n8 supports = 880, r2/r4/r8 steps = 1600/3200/6400
```

Die Schrittzahlen sind innerhalb jedes getrennt/kontinuierlich-Paars exakt
gleich. Jeder Support wird auf jeder Verfeinerung genau einmal zugeordnet.
Die neutralen Luecken enthalten keine synthetischen Nullframes, sondern
korrekt keine Rezeptorabschluesse.

## Evidenzgrenze

Der Planner bestaetigt nur die technische Kontrollierbarkeit des Versuchs.
Er zeigt keine wiederholungsabhaengige E1-Bildung, Praegung, Abschwaechung,
Memory, Feldzeit oder KI.

## Bester naechster Schritt

S1-EC28 sollte den kleinsten E1-Formation-Consumer zunaechst nur mit einer
kurzen synthetischen Planner-Fixture implementieren. Zu pruefen sind
Atomaritaet, Startzustandsidentitaet, Formationablation, Snapshot/Restore
und unveraenderte Eingangsplaene. Noch kein kanonischer `1/2/4/8`-Lauf und
keine Ergebnisentscheidung.
