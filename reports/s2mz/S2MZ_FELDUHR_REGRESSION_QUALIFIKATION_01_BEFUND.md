# S2-MZ: Felduhr-Regression Qualifikation 01

## Entscheidung

Die fokussierte Qualifikation ist `NOT_QUALIFIED`. Die Produktkorrektur
erreichte den direkten Feldadapter erfolgreich, der einzige Testkoerper
brach jedoch danach wegen eines falschen Attributnamens in der Testassertion
ab.

Es gab keinen Retry. Ein weiterer S2-MT-Transferlauf bleibt gesperrt.

## Produktkorrektur

Die Korrektur ist auf zwei private Bindungsstellen begrenzt:

- `build_s2lo_field_adapter` akzeptiert nun optional `field_clock_id`;
- der Standard bleibt unveraendert `s2ln-role-free-field-clock`;
- `ReceptorTimeSequence`, `MCMFieldStepTime` und `CommonFieldTime` verwenden
  innerhalb des Adapters denselben gebundenen Wert;
- S2-MT uebergibt explizit `s2mt-transfer-field-clock`.

Quellen, Zeitwerte, Schwellen, Docks, Rezeptoren, Feldkern, Memory und Kontext
wurden nicht geaendert.

## Einziger Testaufruf

Aus dem Workspace-Root wurde genau einmal ausgefuehrt:

```text
python -m unittest tests.test_s2mz_field_adapter_clock_regression -v
```

Der Aufruf endete mit Exit-Code `1`:

```text
Ran 1 test in 3.463s
FAILED (errors=1)
AttributeError: 'StreamBranchResultV1' object has no attribute 'branch_role'
```

Vor dem Test waren gebunden:

- S2-LO-Runner-SHA-256
  `63f242c96dda024c777e086b4203f4f2d5b69ac8680f7bc03a1a6ba9f389d3aa`;
- S2-MT-Runner-SHA-256
  `9e1774e57dab84eaf37b7d5d289afdc0f01d685d691968acd8be8791c020e7f4`;
- Test-SHA-256
  `f59f7beff1e616e4daa651792ef17d7a62f182b29cb38f1689d75e17427b7b12`.

Die beiden Produktquellhashes blieben nach dem Lauf identisch.

## Erreichter Pfad

Der Fehler entstand erst nach der Rueckkehr aus dem genau einmal direkt
aufgerufenen Feldadapter. Bis zu dieser Testzeile waren bereits erfolgreich
geprueft:

- das qualifizierte `e01`-Materialisat;
- zwei `timed_frames` mit `s2mt-transfer-field-clock`;
- zwei `ReceptorTimeSequence`-Objekte mit derselben Uhr;
- ein `MCMFieldStepTime` ueber das unveraenderte e01-Zeitfenster;
- genau `336` Kontakte in genau `336` Neuroneneingaengen.

Damit ist der urspruengliche Clock-Abbruch technisch geschlossen. Die
nachfolgenden Assertions fuer Branchrolle, publizierten Feldnachzustand,
`CommonFieldTime` und resultierende Rezeptorkontakte wurden im einzigen Lauf
nicht mehr erreicht und gelten deshalb nicht als qualifiziert.

## Testkorrektur

Nach dem fehlgeschlagenen Lauf wurde ausschliesslich die statisch eindeutig
falsche Testassertion von `branch.branch_role` auf das tatsaechliche
unveraenderte Datenfeld `branch.branch` korrigiert. Der korrigierte
Testquellhash lautet:

`7c4514aab5a3efbf33ab1e8a12e4089e85e0f80bf374cebd313d7bedd8174c8f`.

Diese korrigierte Testfassung wurde nicht ausgefuehrt. Sie benoetigt eine
neue, getrennte Qualifikationsfreigabe. Memory, Kontext, S2-MR-Runtime und
S2-MT-Hauptlauf wurden nicht aufgerufen.
