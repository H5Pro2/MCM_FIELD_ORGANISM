# S2-TS: vollständige kanonische Beleggrenze

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-RUN-QUAL-20260919-04`.

Diese Qualifikation bindet die gesamte Serialisierungsgrenze: Aktionen,
Entscheidungen, Offsetfolgen, Baseline-Mitgliedschaften, Digests und leere
verschachtelte Listen. Interne Tupel werden ausschließlich durch den
kanonischen JSON-Schreib-/Leseweg als Listen belegt; Werte, Reihenfolge und
Multiplizität bleiben erhalten.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2ts_temporal_trace_run.py` | `e084f2aa6806337587284df6873068b6366e88eea2f02fc11bc981c143f8387a` |
| `tools/_s2ts_temporal_trace_verification.py` | `9b550b5b492bc5c7a210c9caea91ae1821fa532e6ae137457a88cfa2ff49155c` |
| `tests/test_s2ts_temporal_trace_run.py` | `f17faf0b0fb93e0e71f6c870161092909e8246d64eacaa8c8fc1f79e417d63a6` |

Der einmalige neutrale Aufruf verwendet ausschließlich künstliche Werte. Er
prüft Quellenauflösung, 18 Endpunkte, vollständigen JSON-Rundlauf,
unabhängige Entscheidungen und Baselines sowie manipulierte Quellen, Werte,
Offsets und Baselinefelder. Keine NU-Payload wird materialisiert.
