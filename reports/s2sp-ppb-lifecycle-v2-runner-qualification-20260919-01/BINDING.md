# S2-SP: PPB-Lebenszyklus V2 – Runner-Qualifikation

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-RUNNER-QUAL-20260919-01`.

Einmaliger Aufruf:

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_runner -v
```

Die drei neuen Kontrollen verwenden ausschließlich temporäre neutrale
Payloads. Sie erreichen den vollständigen 20-Ereignis-Record, die getrennten
Arme, unabhängige Verifikation und Auswertung sowie Abweisung einer
unvollständigen Hülle und eines falschen Cue-/Formationsübergangs. OA-Quellen
werden nicht gelesen oder materialisiert.

| Datei | SHA-256 |
|---|---|
| `tools/_s2sp_oa_materialization_adapter.py` | `e06e06ca4a812b0c9182b4e646a1f63000d3b5a7f3be3a0f23251dea09f6e7f1` |
| `tools/_s2sp_ppb_lifecycle_v2_runner.py` | `b923bc8af77a3a31a3d3dcba8e55084abded11a9ac7764bb3e7f4bcd33b36e16` |
| `tests/test_s2sp_ppb_lifecycle_v2_runner.py` | `1257daa787b713d4408bcf9a55d83e3c60e46194ad8309bd77ac0c442819ddda` |

Die bereits bestandene V2-Anschlussqualifikation `8/8` wird referenziert und
nicht erneut ausgeführt. Der reale Lauf bleibt an die separate OA-A–E-
Quellenprüfung und die einmalige Lauf-ID gebunden.
