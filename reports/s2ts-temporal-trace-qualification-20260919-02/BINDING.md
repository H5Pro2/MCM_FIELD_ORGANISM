# S2-TS: Umkehrhint-Qualifikation

Qualifikations-ID: `S2TS-TEMPORAL-TRACE-QUAL-20260919-02`.

Die zwei bestandenen Gruppen aus `...-01` bleiben bei unverändertem
Produktcode gebunden. Dieser einmalige Aufruf führt nur die zuvor nicht
erreichte Ordnungsgruppe aus:

```text
python -B -m unittest tests.test_s2ts_temporal_trace.TemporalTraceTests.test_order_and_fair_baselines -v
```

Die Kontrolle prüft: nach Hintframe `c` ist die Rückgabe `None`, die Spur
bleibt unverändert; erst Hintframe `b` erzeugt `ABSTAIN_ORDER_MISMATCH`; der
temporäre Hintpuffer ist danach leer. Die faire ungeordnete Inhaltsbaseline
bleibt für `b,c` und `c,b` gleich.

| Datei | SHA-256 |
|---|---|
| `tools/_s2ts_temporal_trace.py` | `f197fbcf8ecc3c05c0b38dfe22393b2dcbb3c079fef39431eadde240fff1149a` |
| `tests/test_s2ts_temporal_trace.py` | `f0c6088dba612d9c4092b4391dbc5c98cfe231d3f69d46ad7663989ac00026ee` |
