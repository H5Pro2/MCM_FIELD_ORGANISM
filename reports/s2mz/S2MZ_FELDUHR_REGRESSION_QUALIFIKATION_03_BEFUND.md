# S2-MZ: Felduhr-Regression Qualifikation 03

## Entscheidung

Die Qualifikation
`s2mz-field-clock-regression-20260906-03` ist formal `NOT_QUALIFIED`.

Der einzige Testkoerper bestaetigte erneut den korrigierten Clockpfad, die
Feldbranchrolle, `336` transiente Kontakte, die kontaktfreie
Boundary-Distribution und nicht persistierte Rezeptorkontakte. Er scheiterte
an der vorab gebundenen Erwartung `perception.local_samples == ()`.

Diese Erwartung entspricht nicht der bestehenden Feldsemantik. Es gab keinen
Retry und keine Produkt-, Quellen-, Zeit- oder Fixtureaenderung nach dem
Lauf. Ein weiterer S2-MT-Transferlauf bleibt gesperrt.

## Testbereinigung vor dem Lauf

Vor dem Aufruf wurde ausschliesslich die Testbeobachtung aus Qualifikation 02
bereinigt:

- die Wertgleichheitsschleife zwischen transienten Eingaben und
  `perception.receptor_contact` wurde vollstaendig entfernt;
- `projected.contact_count == 336` blieb gebunden;
- die kontaktfreie Boundary-Distribution wurde explizit geprueft;
- `perception.receptor_contact is None` wurde explizit geprueft;
- `perception.local_samples == ()` wurde entsprechend der Freigabe
  hinzugefuegt;
- Lifecycle, Zustandsdigest und Clockbindungen blieben als Assertions
  erhalten.

Produktmodule, Materialisat und Zeitwerte wurden nicht geaendert.

## Vorbindung

Vor dem Aufruf galten:

- `HEAD == origin/main == 71fbe970bb6ddc3bab969172fd65b0fef659b8b8`;
- S2-LO-Runner-SHA-256
  `63f242c96dda024c777e086b4203f4f2d5b69ac8680f7bc03a1a6ba9f389d3aa`;
- S2-MT-Runner-SHA-256
  `9e1774e57dab84eaf37b7d5d289afdc0f01d685d691968acd8be8791c020e7f4`;
- bereinigter Regressionstest-SHA-256
  `ac9cf4509d67c30123081f4aebbcfdb93aeb75c76e69783b2e30e4d67ab20e5f`.

## Einziger Qualifikationsaufruf

Aus dem Workspace-Root wurde genau einmal ausgefuehrt:

```text
python -m unittest tests.test_s2mz_field_adapter_clock_regression -v
```

Der Prozess endete mit Exit-Code `1`:

```text
Ran 1 test in 3.416s
FAILED (failures=1)
AssertionError: False is not true
```

Die fehlgeschlagene Zeile pruefte:

```python
all(neuron.perception.local_samples == () for neuron in neurons.values())
```

## Bestaetigte Pruefungen

Vor dieser Assertion waren bereits erfolgreich bestaetigt:

- S2-LN-Standardclock unveraendert;
- beide e01-Sequenzen an `s2mt-transfer-field-clock` gebunden;
- Feldschritt und publizierte Feldzeit stimmen mit e01 ueberein;
- Feldbranchrolle `FIELD`;
- Postzustand `COMPLETED`, Schrittzahl `1`;
- genau `336` Kontakte und `336` Neuroneneingaenge;
- persistente Boundary-Distribution hat keine Kontakte;
- jedes `perception.receptor_contact` ist `None`.

Die danach angeordnete Assertion zum vom Nullzustand abweichenden
Postzustandsdigest wurde im Testlauf nicht mehr erreicht und wird daher fuer
diese Qualifikation nicht als bestanden ausgegeben.

## Statischer Ursachenbefund

`MCMNeuronLayer._perception_for` bildet `local_samples` fuer jeden
Feldteilnehmer aus den durch `sample_offsets` erreichbaren benachbarten
Feldneuronen. Diese lokalen Feldsamples sind von `receptor_contact` und vom
separaten `TransientNeuronInputSet` verschieden. Der S2-LO-Feldschritt
verwendet weiterhin die vorhandene nichtleere Nachbarschaftsgeometrie.

Deshalb belegt eine kontaktfreie Boundary-Distribution zwar korrekt
`receptor_contact is None`, nicht aber leere `local_samples`. Die
Qualifikation darf nicht durch Umdeutung des fehlgeschlagenen Tests bestanden
gesetzt werden. Memory, Kontext, S2-MR-Runtime und S2-MT-Hauptlauf wurden
nicht aufgerufen.
