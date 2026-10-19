# S2-TS: vollständige Anschlussqualifikation nach Entwicklungsprüfung

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-RUN-QUAL-20260919-05`.

Vor dem formalen Aufruf bestanden neutrale Entwicklungstests ausschließlich
gegen künstliche 48-Wert-Frames. Die neue formale Suite prüft gemeinsam
Ereignisfolge, NU-Planauflösung, JSON-Rundlauf, Quellen-/Wert-/Offset- und
Baseline-Manipulation sowie die unabhängige Direktrechnung.

| Datei | SHA-256 | Byte |
| --- | --- | ---: |
| `tools/_s2ts_temporal_trace.py` | `64d1e7f9ff54d898996974d960bfb58ac7386165846aeec0ea253079e0a8e6d8` | 4.078 |
| `tools/_s2ts_temporal_trace_run.py` | `e084f2aa6806337587284df6873068b6366e88eea2f02fc11bc981c143f8387a` | 10.468 |
| `tools/_s2ts_temporal_trace_verification.py` | `2672a02befdd0f37c5bde304dd040666310219f7f006f8a8302cb54d406f8693` | 6.362 |
| `tests/test_s2ts_temporal_trace_run.py` | `6e425cfeba07a408b8af38819d7fd7400a8c51a740c5c3f5d78a1e9de05f52c1` | 4.527 |

Die reale Hülle bleibt auf 20 Ereignisse, 18 Endpunkte/Analysen/NJ-Projektionen,
0 Feldkontakte, 0 Scans und maximal 262.144 Record-Bytes begrenzt. Das
Quellenausführungsdokument bleibt durch SHA-256
`6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`
gebunden.
