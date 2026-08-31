# S2-HJ: Neutrale Qualifikation der kompakten Projektionen

Status: `S2HJ_QUALIFICATION_FAILED_FIXTURE_ENVELOPE_OVERSIZE`

## Umfang

S2-HJ war ausschliesslich als neutrale Qualifikation der drei kompakten
Aufzeichnungsprojektionen vorgesehen. Vorregistriert waren zwoelf Tests fuer:

- 52 Formation-, vier S2-GC- und vier S2-GI-Projektionsrollen;
- die Grenzen 2.801, 3.174 und 2.977 Byte sowie die 4.096-Byte-Registrygrenze;
- Quellen-, Owner-, Eltern-, Nachfolger- und Receipt-Digests;
- gezielte Mutationen des `owner_prestate_digest`, des Sequence-Evidence-Digests
  und der Formationkette;
- Unveraendertheit der synthetischen vollstaendigen In-Memory-Belege;
- unveraenderte Budgets, Fehlergrenzen und das geschlossene Hauptgate;
- den dauerhaft nicht auswertbaren Status von S2-HC.

Die Fixture verwendete ausschliesslich synthetische, bereits gebundene
In-Memory-Belege. Sie rief keine Rezeptor-, Speicher-, Koordinator-,
Kontextverbraucher- oder Kontextauswertungsfunktion auf. Keine S2-GJ-Geschichte
wurde materialisiert oder ausgefuehrt.

## Einmaliger Lauf

Qualifikations-ID:

`s2hj-compact-projection-qualification-20260831-01`

Es erfolgte genau ein Aufruf:

```text
python -m unittest tests.test_s2hj_compact_projection_qualification -v
```

Ergebnis:

```text
Exit-Code: 1
Tests ausgefuehrt: 0
Fehler: 1 in setUpClass
```

Der Abbruch entstand bei der neutralen Materialisierung einer S2-GC-Huelle.
Die Qualifikationsfixture hatte fuer die Huelle eine kuenstlich bis nahe an die
allgemeine ID-Grenze verlaengerte Owner-ID verwendet. Diese zusaetzlichen Bytes
liessen die synthetische S2-GC-Huelle die gebundene Rollenobergrenze von 3.174
Byte ueberschreiten. `_validate_compact_envelope_size` stoppte korrekt mit
`E008`.

Damit wurde weder ein Projektionsvalidator noch eine Digestmutation fachlich
negativ bewertet. Der Lauf erreichte die zwoelf Testkoerper nicht. S2-HJ ist
dennoch nicht bestanden, weil die vorregistrierte neutrale Qualifikation nicht
vollstaendig ausgefuehrt wurde.

## Unveraendertheit

Die SHA-256-Digests von Runner, Verifikator, Recorder, Fixture-Registry und
Testdatei waren vor und nach dem einzigen Aufruf identisch. Insbesondere blieben
unveraendert:

```text
MAIN_EXECUTION_ENABLED = False
MAX_SUCCESS_PATH_BYTES = 2.009.088
MAX_FAILURE_PATH_BYTES = 2.045.952
MAX_RUN_PATH_BYTES     = 2.045.952
```

S2-HC bleibt unveraendert `NOT_EVALUABLE`. Es fand kein Funktionslauf statt.

## Entscheidung

Status:

`S2HJ_QUALIFICATION_FAILED_FIXTURE_ENVELOPE_OVERSIZE`

Der Fehler liegt in der neutralen Qualifikationsfixture, nicht in einem
Memory- oder Kontextfunktionsbefund. Entsprechend der Einmalregel wurde weder
nachkorrigiert noch wiederholt.

Der naechste zulaessige Schritt ist eine separat freizugebende neue
Qualifikation unter neuer ID. Sie darf ausschliesslich die neutrale Owner-ID der
Fixture auf eine gebundene, realistische Laenge korrigieren; die vier
S2-GT-Produktionsmodule und die zwoelf Pruefziele bleiben dabei unveraendert.
Ein neuer Kontextfunktionslauf bleibt gesperrt.
