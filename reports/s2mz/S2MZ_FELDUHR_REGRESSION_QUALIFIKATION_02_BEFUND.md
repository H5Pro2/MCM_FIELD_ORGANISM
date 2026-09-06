# S2-MZ: Felduhr-Regression Qualifikation 02

## Entscheidung

Die Qualifikation
`s2mz-field-clock-regression-20260906-02` ist formal `NOT_QUALIFIED`.

Der korrigierte Clockpfad und alle vier freigegebenen Kernpruefungen wurden
im einzigen Testkoerper erfolgreich durchlaufen. Der Test scheiterte erst an
einer zusaetzlichen, fachlich falschen Assertion zur persistenten
Feldrepraesentation transienter Dockkontakte. Es gab keinen Retry und keine
Quell-, Produkt-, Zeit- oder Fixtureaenderung.

Ein weiterer S2-MT-Transferlauf bleibt gesperrt.

## Vorbindung

Vor dem Aufruf galten:

- `HEAD == origin/main == 0b11ac5ebc694b9dcc9f33fa59fdb439d4830a3f`;
- S2-LO-Runner-SHA-256
  `63f242c96dda024c777e086b4203f4f2d5b69ac8680f7bc03a1a6ba9f389d3aa`;
- S2-MT-Runner-SHA-256
  `9e1774e57dab84eaf37b7d5d289afdc0f01d685d691968acd8be8791c020e7f4`;
- Regressionstest-SHA-256
  `7c4514aab5a3efbf33ab1e8a12e4089e85e0f80bf374cebd313d7bedd8174c8f`;
- nur die bekannte ausgeschlossene Bootstrap-Datei war unversioniert.

Alle drei Hashes waren nach dem Lauf unveraendert.

## Einziger Qualifikationsaufruf

Aus dem Workspace-Root wurde genau einmal ausgefuehrt:

```text
python -m unittest tests.test_s2mz_field_adapter_clock_regression -v
```

Der Prozess endete mit Exit-Code `1`:

```text
Ran 1 test in 3.559s
FAILED (failures=1)
AssertionError: 2.0882934892730242e-05 != None
```

## Bestaetigte Kernpruefungen

Vor der fehlgeschlagenen Zusatzassertion waren bereits erfolgreich
bestaetigt:

- der Adapterstandard bleibt `s2ln-role-free-field-clock`;
- das qualifizierte `e01` bindet zwei `timed_frames` an
  `s2mt-transfer-field-clock`;
- beide `ReceptorTimeSequence`-Objekte verwenden diese explizite Uhr;
- `MCMFieldStepTime` und publizierte `CommonFieldTime` stimmen in Uhr,
  Starttick und Endtick mit `e01` ueberein;
- die Feldbranchrolle ist `FIELD`;
- der Nachzustand ist `COMPLETED`, Schritt `1`;
- genau `336` transiente Kontakte wurden auf genau `336`
  Neuroneneingaenge projiziert.

Damit ist der urspruengliche Clockfehler technisch nicht wieder
aufgetreten.

## Ursache des Testfehlers

Die letzte Zusatzpruefung setzte jeden transienten Kontaktwert mit
`neuron.perception.receptor_contact` gleich. Der S2-LO-Feldpfad verwendet
jedoch absichtlich eine kontaktfreie persistente `ReceptorDistribution` und
uebergibt die `336` Werte separat als `TransientNeuronInputSet` an den
Feldschritt. Daher bleibt `perception.receptor_contact` in diesem Pfad
korrekt `None`; der transiente Wert wirkt in der Feldintegration und wird
nicht als persistenter Distributionskontakt umetikettiert.

Diese Assertion gehoerte nicht zu den vier freigegebenen Kernpruefungen,
macht den `unittest`-Lauf mit Exit-Code `1` aber formal unqualifiziert. Sie
wurde nach dem Lauf nicht geaendert. Memory, Kontext, S2-MR-Runtime und
S2-MT-Hauptlauf wurden nicht aufgerufen.
