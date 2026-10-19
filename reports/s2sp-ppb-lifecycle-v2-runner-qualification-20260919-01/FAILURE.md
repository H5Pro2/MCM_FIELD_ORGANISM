# S2-SP: PPB-Lebenszyklus V2 – Runner-Qualifikation fehlgeschlagen

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-RUNNER-QUAL-20260919-01`.

Der einmalige Aufruf endete nach `0.820 s` mit `Ran 0 tests` in `setUpClass`.
Die drei neuen Prüfgruppen wurden nicht erreicht.

Der neue Adapter `bind_materialized_input()` las für die gemeinsame
Zeitbindung fälschlich `window_start_tick` und `window_end_tick` direkt von
`S2LOFieldInputV1`. Dieser Typ besitzt diese Attribute nicht. Der Fehler
lautet:

```text
AttributeError: 'S2LOFieldInputV1' object has no attribute 'window_start_tick'
```

Das ist ein Fehler der neu ergänzten Adapterdarstellung, kein Befund gegen
die Materialisierung, Memorymechanik oder die OA-Quellen. Die reale
V2-Materialisierung wurde nicht aufgerufen, kein Ergebnisverzeichnis für den
V2-Hauptlauf erzeugt und kein V2-Vergleich ausgeführt. Kein Retry erfolgt.
