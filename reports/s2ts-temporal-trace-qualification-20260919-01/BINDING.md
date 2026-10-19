# S2-TS: neutrale Spurzustands-Qualifikation

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-QUAL-20260919-01`.

Einmaliger Aufruf:

```text
python -B -m unittest tests.test_s2ts_temporal_trace -v
```

| Datei | SHA-256 |
|---|---|
| `tools/_s2ts_temporal_trace.py` | `f197fbcf8ecc3c05c0b38dfe22393b2dcbb3c079fef39431eadde240fff1149a` |
| `tests/test_s2ts_temporal_trace.py` | `cf2e3f61e3714f337058982e3e560e5fb97740c7edf9aea39ad3e8c96073883c` |

Die drei Tests verwenden nur neutrale 48-Wert-Fixtures. Sie prüfen geordnete
Wiederfindung gegen die faire Inhaltsbaseline, Nichtnachbarschaft,
Mehrfachoffset, Kapazitäts- und Sitzungsverfall sowie Hintpuffer-
Unveränderlichkeit. NU-Payloads, NJ, Rezeptor, Feld und A/B-Memory bleiben
ausgeschlossen.
