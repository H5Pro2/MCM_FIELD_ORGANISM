# S2-SP: PPB-Lebenszyklus V2 – native Feldbindungs-Kontrolle

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-RUNNER-QUAL-20260919-04`.

Der fehlgeschlagene Befund `...-03` bleibt unverändert. Die folgenden drei
Runner-Kontrollen waren dort mit unverändertem Produktcode erfolgreich und
werden nicht wiederholt:

1. vollständige neutrale Runner-Hülle;
2. unvollständige Hülle vor Memoryfortschreibung;
3. falsche Art an einer Cue-Position.

Dieser einmalige Aufruf erreicht ausschließlich die zuvor nicht erreichte
native Feldbindungs-Kontrolle:

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_runner.S2SPPpbLifecycleV2RunnerTests.test_rejects_invalid_native_field_binding -v
```

Die Fixture hält native `oa.Input`-Materialisate und adaptierte
`S2SPOAMaterializedPairV1`-Belege getrennt. Die Negativkontrolle verändert
nur das Feld `field_payload` eines nativen Eingangs und übergibt diesen an
`bind_materialized_input()`. Sie ergänzt kein künstliches `event`-Attribut.

Vor dem Aufruf bestätigten CPython-Kompilierung und AST-Prüfung die Trennung
der beiden Belegformen sowie den tatsächlichen Adapteraufruf.

| Datei | SHA-256 |
|---|---|
| `tools/_s2sp_oa_materialization_adapter.py` | `f47829c96094cb1979cbd94d1990a100aef6b574b6fb5ed8c3d3746ab147612c` |
| `tools/_s2sp_ppb_lifecycle_v2_runner.py` | `b923bc8af77a3a31a3d3dcba8e55084abded11a9ac7764bb3e7f4bcd33b36e16` |
| `tests/test_s2sp_ppb_lifecycle_v2_runner.py` | `c18c498e38193747871ce06d118a26a34800d7c8512a0987a84049b8e956389b` |

Die Produktdateien sind gegenüber `...-03` unverändert. Der Testhash ändert
sich ausschließlich durch die zusätzliche native Fixturebindung und die
korrigierte Negativkontrolle.
