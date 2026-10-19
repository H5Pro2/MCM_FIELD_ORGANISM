# S2-TS-Laufanschlussqualifikation

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-RUN-QUAL-20260919-01`.

Die vorhandene Spurzustandsqualifikation `...-02` bleibt mit `3/3` gebunden;
dieser eine Aufruf prüft ausschließlich die neue Ereignis-/Quellenanbindung.

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2ts_temporal_trace.py` | `64d1e7f9ff54d898996974d960bfb58ac7386165846aeec0ea253079e0a8e6d8` |
| `tools/_s2ts_temporal_trace_run.py` | `ffc4220fd96ad888213bec3289400b304aff7ed689faeaa3c7b5e366263fa4d6` |
| `tests/test_s2ts_temporal_trace_run.py` | `ebb73a849281c233bf0b561c8acfaf742aeed983e3d589bc372c41b3375be0aa` |
| `docs/ZEITSPUR_TEILVERLAUF_STATIC_PLAN.md` | `7f76370da52b7720b885ea06a39f117de1ba9f452186300addd0a7ddd67872f6` |

Gebunden sind 20 Ereignisse: 18 vorversiegelte NU-Quellennutzungen, acht
Formationen, zehn Hintframes und zwei Close-Ereignisse. Die Hülle begrenzt
die spätere reale Verarbeitung auf 18 Analysen, 18 NJ-Projektionen, null
Feldkontakte und null A/B-Scans. Der neutrale Aufruf verwendet nur künstliche
48-Wert-Frames und öffnet keine NU-Payload.
