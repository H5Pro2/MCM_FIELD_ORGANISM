# S2-MK: Neutrale Messqualifikation

## Status

`S2MK_NEUTRAL_MOTION_MEASUREMENT_NOT_QUALIFIED`

Die einmalige Qualifikation
`s2mk-neutral-motion-measurement-qualification-20260905-01` wurde genau
einmal gestartet und nicht wiederholt.

## Statischer Preflight

- eindeutige Testkoerper: `15`;
- Referenzen auf den versiegelten S2-MJ-Korpus: `0`;
- Produktimporte von Memory, Kontext oder Feld: `0`;
- S2-MK-Ergebnisverzeichnis vor dem Aufruf vorhanden: `False`.

Produkt- und Testhashes vor dem Aufruf:

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2mk_private_motion_measurement.py` | `5cbdc171d5ada36ef2d802e82af58e129a51f1b191a4f086fa9dcf11d79ae595` |
| `tests/test_s2mk_private_motion_measurement.py` | `ff23ae31c82f7366a6558e3a3142d850a72f4c17f12987afbd2e8061268e9f58` |

## Einmaliger Aufruf

```text
.venv/Scripts/python.exe -m unittest -v tests.test_s2mk_private_motion_measurement
```

- Aufrufe: `1`;
- Exit-Code: `1`;
- ausgefuehrte Testkoerper: `0/15`;
- terminales unittest-Ergebnis: `FAILED (errors=1)`.

Der Abbruch entstand in `setUpClass`, bevor `measure_and_compare` erreicht
wurde:

```text
baseline_working_set = _working_set_bytes()
OSError: GetProcessMemoryInfo failed
```

Die neutrale Windows-Working-Set-Abfrage konnte ihre ABI-Bindung nicht
materialisieren. Deshalb liegen weder eine Peakmessung noch ein
Qualifikationsbefund ueber RGB-zu-Y, Flow, Interpolation, Residuen,
Zellabdeckung oder Baselines vor.

## Nicht ausgefuehrte Funktion

Bis zum Setupabbruch gelten:

```text
corpus_pairs_opened = 0
flow_calls          = 0
receptor_calls      = 0
memory_calls        = 0
context_calls       = 0
field_calls         = 0
```

Der zuvor qualifizierte OpenCV-Build wurde gebunden. Das neutrale
Vollformatpaar wurde im Testprozess erzeugt, aber nicht an die Messfunktion
uebergeben.

## Hashvergleich

Die Quellhashes nach dem Aufruf sind mit den Vorhashes identisch:

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2mk_private_motion_measurement.py` | `5cbdc171d5ada36ef2d802e82af58e129a51f1b191a4f086fa9dcf11d79ae595` |
| `tests/test_s2mk_private_motion_measurement.py` | `ff23ae31c82f7366a6558e3a3142d850a72f4c17f12987afbd2e8061268e9f58` |

## Entscheidung

Die private S2-MK-Implementierung ist statisch vorbereitet, aber nicht
technisch qualifiziert. Die acht vorversiegelten S2-MJ-Paare bleiben
ungeoeffnet und ihr Lauf bleibt gesperrt.

Eine Korrektur darf ausschliesslich die neutrale Windows-Speichermessfixture
betreffen. Sie benoetigt eine neue Qualifikations-ID und einen neuen,
separat freigegebenen Einmalaufruf. Aus diesem Setupfehler folgt kein Befund
ueber die Bewegungsmessung oder die MCM-Funktion.
