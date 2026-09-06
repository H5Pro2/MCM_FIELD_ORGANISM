# S2-MZ: Felduhr-Regression Qualifikation 04

## Entscheidung

Die Qualifikation
`s2mz-field-clock-regression-20260906-04` ist bestanden.

Der genau einmal ausgefuehrte fokussierte Regressionstest endete mit
Exit-Code `0`, `1/1` und `OK`. Die S2-MT-Felduhrkorrektur ist damit fuer den
direkten S2-LO-Feldadapter qualifiziert.

Es gab keinen Retry. Ein weiterer S2-MT-Transferlauf wurde nicht ausgefuehrt
und benoetigt eine separate Freigabe.

## Testgrenze

Der Test wurde vor dem Lauf ausschliesslich auf seinen gebundenen Zweck
reduziert. Assertions zu `perception.receptor_contact` und
`perception.local_samples` wurden vollstaendig entfernt. Geprueft wurden nur:

- explizite S2-MT-Felduhr;
- unveraenderter S2-LN-Standard;
- Feldbranchrolle `FIELD`;
- genau `336` Kontakte in genau `336` transienten Neuroneneingaengen;
- kontaktfreie Boundary-Distribution;
- Postzustand `COMPLETED`, Schrittzahl `1` und korrekte Endzeit;
- vom Nullzustand verschiedener Feldzustandsdigest.

Produktmodule, Quellen, Materialisat, Zeitwerte, Schwellen und Feldkern
blieben unveraendert.

## Vorbindung

Vor dem Aufruf galten:

- `HEAD == origin/main == c1d6e6d793cee252017d46c517df70b3a7587325`;
- S2-LO-Runner-SHA-256
  `63f242c96dda024c777e086b4203f4f2d5b69ac8680f7bc03a1a6ba9f389d3aa`;
- S2-MT-Runner-SHA-256
  `9e1774e57dab84eaf37b7d5d289afdc0f01d685d691968acd8be8791c020e7f4`;
- reduzierte Regressionstest-SHA-256
  `5b754bbec523c78bb8de09c4afe73b55e40d6e61ffabaedc8140f8b0d1403edf`.

Die beiden Produktquellhashes waren gegenueber den Qualifikationen 02 und 03
unveraendert.

## Einziger Qualifikationsaufruf

Aus dem Workspace-Root wurde genau einmal ausgefuehrt:

```text
python -m unittest tests.test_s2mz_field_adapter_clock_regression -v
```

Das Ergebnis lautete:

```text
test_e01_uses_bound_clock_and_default_remains_s2ln ... ok
Ran 1 test in 3.360s
OK
```

Der Prozess endete mit Exit-Code `0`.

## Bestaetigter Feldpfad

Das qualifizierte `e01`-Materialisat fuehrte ueber den explizit mit
`s2mt-transfer-field-clock` gebauten Adapter zu einem vollstaendigen
Feldbranchresultat. Beide `ReceptorTimeSequence`-Objekte, der
`MCMFieldStepTime` und die publizierte `CommonFieldTime` banden dieselbe Uhr
und dasselbe e01-Zeitfenster.

Die transiente Projektion umfasste genau `336` Kontakte und `336`
Neuroneneingaenge. Die persistente Boundary-Distribution blieb kontaktfrei.
Der Feldnachzustand war `COMPLETED`, Schritt `1`, endete am gebundenen
e01-Endtick und besass einen vom frischen Nullzustand verschiedenen Digest.

Der ohne Argument gebaute S2-LO-Adapter band weiterhin exakt
`s2ln-role-free-field-clock`. Memory, Kontext, S2-MR-Runtime und
S2-MT-Hauptlauf wurden nicht aufgerufen.
