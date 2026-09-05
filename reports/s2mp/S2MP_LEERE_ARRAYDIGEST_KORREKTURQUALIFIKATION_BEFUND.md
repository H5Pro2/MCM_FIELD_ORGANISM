# S2-MP: Qualifikation der leeren Arraydigestform

Status: `S2MP_EMPTY_VALID_COMPONENT_DIGEST_VALID`

Die enge Korrektur an `_array_digest` ist unter der Qualifikations-ID
`s2mp-neutral-empty-array-digest-qualification-20260905-01` qualifiziert.

## Produktkorrektur

Die kanonische Bytebildung verwendet jetzt ausschliesslich:

```python
canonical.tobytes(order="C")
```

Leere Arrays ergeben damit regulaer SHA-256 ueber die leere Bytefolge:
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
Nichtleere Referenzarrays bleiben gegenueber der bisherigen
`memoryview(...).cast("B")`-Form bytegleich.

Detektor, PyrLK, Schwellen, Evidenzstatus, Rollen, Formen und Zaehler wurden
nicht geaendert.

## Einmalqualifikation

Aufruf:

```text
.venv/Scripts/python.exe -m unittest -v tests.test_s2mp_private_empty_array_digest_qualification
```

Ergebnis:

```text
Ran 5 tests in 0.399s
OK
Exit-Code 0
```

Die fuenf Tests prueften:

1. leere `(0, 2)`-Punktprojektionen;
2. leere Index-, Fehler- und Residuenvektoren;
3. mindestens einen Kandidaten bei null gueltigen Tracks;
4. `INSUFFICIENT_MOTION_EVIDENCE` mit vollstaendigen Rollen-, Form- und Zaehlerbindungen;
5. unveraenderte Digests nichtleerer Punkt-, Index-, Status-, Fehler- und Residuenreferenzen.

## Hashbindung

| Artefakt | SHA-256 vor und nach dem Lauf |
| --- | --- |
| Produktmodul | `a8d2d6d66aa08b173a3a848ef2b5f5488694ecdabd9d2f78c13a3211ee500955` |
| Testdatei | `7105bc896e15463ce4e130a7a6de753bab338015f7787f002b7ee1137096a261` |

Der fruehere S2-MQ-Lauf `...-02` bleibt unveraendert `NOT_EVALUABLE`.
