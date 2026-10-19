# S2-SP: PPB-Lebenszyklus V2 – Runner-Qualifikation nach lokaler Feldbindung

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-RUNNER-QUAL-20260919-03`.

Die Fehlbefunde `...-01` und `...-02` bleiben unverändert. Dieser einmalige
Aufruf erreicht ausschließlich die vier bisher nicht erreichten neutralen
Runnerkontrollen:

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_runner -v
```

Vor dem Aufruf wurden die drei gebundenen Dateien mit CPython kompiliert und
per AST geprüft: In `bind_materialized_input()` wird `field_input` vor dem
ersten Zugriff aus `event.field_payload` gebunden. `ruff`, `pyflakes`, `mypy`
und `pylint` sind in diesem Workspace nicht installiert; sie wurden nicht als
ausgeführt ausgegeben.

| Datei | SHA-256 |
|---|---|
| `tools/_s2sp_oa_materialization_adapter.py` | `f47829c96094cb1979cbd94d1990a100aef6b574b6fb5ed8c3d3746ab147612c` |
| `tools/_s2sp_ppb_lifecycle_v2_runner.py` | `b923bc8af77a3a31a3d3dcba8e55084abded11a9ac7764bb3e7f4bcd33b36e16` |
| `tests/test_s2sp_ppb_lifecycle_v2_runner.py` | `fe34e273781a43dd02fafed55b90929b3be0039080a8768dc0cb068c87c0ab1a` |

## Prüfbestand

1. Vollständige neutrale 20-Ereignis-Hülle erreicht Verifikation und getrennte
   Auswertung.
2. Unvollständige Hülle wird vor jeder Memoryfortschreibung abgewiesen.
3. Eine falsche Art an einer gebundenen Cue-Position wird abgewiesen.
4. Ein falscher nativer `S2LOFieldInputV1` wird abgewiesen.

Die Fixtures verwenden temporäre neutrale Eingaben. Es werden weder OA-Quellen
noch reale V2-Materialisate verarbeitet.
