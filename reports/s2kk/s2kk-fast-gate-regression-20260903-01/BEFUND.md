# S2-KK Fast-Gate-Regression

## Status

`S2KK_NATIVE_FAST_SEPARATION_GATE_VALID`

Qualifikations-ID: `s2kk-fast-gate-regression-20260903-01`

Das prospektive Distraktor-Startgate verwendet jetzt exakt die Negation der
nativen gemeinsamen Fast-Zuordnung:

```text
Fast-Match: auditory_distance <= 0.2 AND visual_distance <= 0.2
getrennt:   auditory_distance > 0.2 OR  visual_distance > 0.2
```

## Einmalige Qualifikation

```text
python -m unittest tests.test_s2kk_fast_separation_gate -v

Ran 1 test in 1.621s

OK
EXIT_CODE=0
```

Der Test materialisierte die reale gebundene S2-KK-Fixture mit allen 19
AV-Bloecken und pruefte:

- 27 Beziehungen `D1..D9` gegen `T_PLUS/T_MINUS/H_FULL`;
- 36 Distraktorpaare;
- insgesamt 63 Beziehungen und exakt null gemeinsame Fast-Matches;
- OR-Trennung bei nur einer ueberschrittenen Modalitaet;
- Ablehnung, wenn beide Modalitaeten innerhalb ihrer Fast-Schwelle liegen.

Es erfolgte kein Memory-, Kontext- oder Feldaufruf. Es gab keinen Retry und
keine Nachkorrektur. Die Quellhashes waren vor und nach dem Test identisch:

| Datei | SHA-256 |
| --- | --- |
| `_s2kk_context_utility_fixtures.py` | `6b6954381a85704efb6a87c4f1a6a3c49c4d04b4410d19cc3814b0d4077386f6` |
| `test_s2kk_fast_separation_gate.py` | `e6a119e802030f5a6d8a53767adc0e45114793e6f3154831ad637b2c1db598da` |

Der abgeschlossene Lauf `s2kk-functional-20260903-01` bleibt unveraendert
`NOT_EVALUABLE`. Ein neuer `17/1/1`-Lauf benoetigt eine neue Lauf-ID und
separate Freigabe.
