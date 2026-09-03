# S2-KK Fast-Gate-Distanzdiagnose

## Status

`S2KK_FAST_GATE_DIAGNOSIS_CONFIRMS_OR_SEPARATION`

Diagnose-ID: `s2kk-distance-diagnosis-20260903-01`

Die einmalige read-only Diagnose materialisierte die gebundenen
Rezeptorwerte ohne Memory-, Kontext- oder Feldaufruf.

## Ergebnis

| Relation | Anzahl |
| --- | ---: |
| `D1..D9` gegen `T_PLUS/T_MINUS/H_FULL` | 27 |
| Distraktorpaare | 36 |
| Gesamt | 63 |
| gemeinsamer Fast-Match | 0 |
| durch die echte Fast-Regel getrennt | 63 |
| vom bisherigen Startgate akzeptiert | 0 |

Messbereiche:

```text
auditive Distanz: 0.046051827674693784 .. 0.07273487587711298
visuelle Distanz: 0.49319172113289755  .. 0.5486111111111112
visuell D/Anker:  0.49319172113289755  .. 0.49779411764705883
```

Die native Fast-Zuordnung verlangt gleichzeitig:

```text
auditory_distance <= 0.2 AND visual_distance <= 0.2
```

Damit ist die korrekte Trennungsregel:

```text
auditory_distance > 0.2 OR visual_distance > 0.2
```

Das im abgeschlossenen Lauf verwendete Gate verlangte dagegen beide
Einzeldistanzen oberhalb `0.2`. Es wies deshalb alle 63 gueltig getrennten
Beziehungen ab. Der Ergebnisdigest der Diagnose lautet
`41ac41861f778f788fc4fb2cb13413817f6c485dc8367cb01c5999a491fd9cb7`.

S2-KK-Memory wurde nicht aufgerufen. Der Lauf
`s2kk-functional-20260903-01` bleibt unveraendert `NOT_EVALUABLE`.
