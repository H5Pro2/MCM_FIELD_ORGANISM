# S2-MK: Neutrale Messqualifikation 02

## Status

`S2MK_NEUTRAL_MOTION_MEASUREMENT_NOT_QUALIFIED`

Die Qualifikation
`s2mk-neutral-motion-measurement-qualification-20260905-02` wurde genau
einmal gestartet und nicht wiederholt. Der historische erste Versuch bleibt
unveraendert erhalten.

## Freigegebene Aenderung

Ausschliesslich die neutrale Windows-Speichermessfixture wurde geaendert:

- `kernel32` und `psapi` werden mit `ctypes.WinDLL(...,
  use_last_error=True)` geladen;
- `GetCurrentProcess.restype` ist `wintypes.HANDLE`;
- `GetProcessMemoryInfo` besitzt vollstaendige `argtypes` und
  `restype = wintypes.BOOL`;
- die x64-Struktur ist vor der Messung auf `72` Byte und die Offsets
  `0,4,8,16,24,32,40,48,56,64` gebunden;
- Win32-Fehler werden ueber `ctypes.get_last_error()` und
  `ctypes.WinError(...)` weitergegeben;
- Fehler des Sampling-Threads werden nach `join()` im Hauptthread
  weitergegeben.

Die 15 Testmethoden und das Produktmodul blieben unveraendert.

## Quellhashes vor dem Lauf

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2mk_private_motion_measurement.py` | `5cbdc171d5ada36ef2d802e82af58e129a51f1b191a4f086fa9dcf11d79ae595` |
| `tests/test_s2mk_private_motion_measurement.py` | `862982988692dbc413c8083b9e9defb4ec788226a24ecd093d39b9442afbf3be` |

## Einmaliger Aufruf

```text
.venv/Scripts/python.exe -m unittest -v tests.test_s2mk_private_motion_measurement
```

- Aufrufe: `1`;
- Exit-Code: `1`;
- ausgefuehrte Testkoerper: `0/15`;
- terminales unittest-Ergebnis: `FAILED (errors=1)`.

Die ABI-Korrektur war wirksam. `GetProcessMemoryInfo` lieferte erfolgreich
den Ausgangswert, der Sampling-Thread startete und der Produktpfad erreichte:

- zwei Flowaufrufe auf dem neutralen Vollformatpaar;
- zwei visuelle Rezeptoraufrufe;
- zwei Pose-/Formprojektionen;
- keinen Zugriff auf die acht versiegelten Korpuspaare;
- keine Memory-, Kontext- oder Feldfunktion.

## Abbruch

Der Lauf brach in `compute_independent_baselines` ab, bevor
`measure_and_compare` einen Ergebnisbeleg zurueckgeben konnte:

```text
TypeError: unsupported operand type(s) for -: 'tuple' and 'tuple'
```

Betroffen ist die Bildung von `pose_absolute_differences`.
`PoseV1.background_channels` ist ein Tupel aus drei Floatwerten, wird im
S2-MK-Produktmodul aber wie ein einzelner Skalar subtrahiert. Die uebrigen
Posefelder sind skalare Werte.

Dies ist kein ABI-, Korpus-, Flow-, Rezeptor-, Memory-, Kontext- oder
Feldbefund. Es ist ein enger Produktfehler in der noch unqualifizierten
Baselineprojektion. Wegen des Setupabbruchs sind auch die zuvor erzeugten
neutralen Flow- und Rezeptorzwischenwerte nicht qualifiziert.

## Quellhashes nach dem Lauf

| Quelle | SHA-256 |
| --- | --- |
| `tools/_s2mk_private_motion_measurement.py` | `5cbdc171d5ada36ef2d802e82af58e129a51f1b191a4f086fa9dcf11d79ae595` |
| `tests/test_s2mk_private_motion_measurement.py` | `862982988692dbc413c8083b9e9defb4ec788226a24ecd093d39b9442afbf3be` |

## Entscheidung

S2-MK bleibt technisch nicht qualifiziert. Die acht vorversiegelten
S2-MJ-Paare bleiben ungeoeffnet und ihr Lauf bleibt gesperrt.

Eine weitere Korrektur benoetigt eine neue Freigabe. Sie darf nur die
kanonische komponentenweise Behandlung von `background_channels` in der
unabhaengigen Posebaseline und die dazugehoerige unveraenderliche
Ausgabeform betreffen. Ein neuer Testaufruf benoetigt eine neue
Qualifikations-ID.
