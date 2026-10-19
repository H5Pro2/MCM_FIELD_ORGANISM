# S2-TY Real Entry: gebundene neutrale Anschlussqualifikation

Kennung: `s2ty-real-entry-qualification-20260920-02`. Erwartet werden 25
Tests aus `tests.test_s2ty_real_source_supplier`, `tests.test_s2ty_evaluation`,
`tests.test_s2ty_run_envelope` und `tests.test_s2ty_real_run_entry`.

Die Prüfung verwendet ausschließlich neutrale In-Memory-Fenster, ersetzte
Lieferanten und temporäre Ausgaben. Sie erreicht keine NU-/TW-Payload, keinen
Hauptlauf und keine reale Ergebnisablage. Sie prüft Quellen-Lazy-Bindung,
Hash/Analyse/NJ-Zähler, vollständige Vorbilanz, vorhandene Ausgabe,
Materialisierungsabbruch, äußere Verifikationssperre, Auswertungssperre und
Gate-Rücksetzung.

Gebundene Hashes: `_s2ty_real_run_entry.py`
`e16bef74d752ee4bbd179be3b4d0b95dcde1b32feb188a697955e3cbadc4aed9`,
`_s2ty_run_envelope.py`
`151f4f08c2141bd0ffb3b69e183a3a8bb20bbd32acc863b48cc0da016347866b`,
`_s2ty_real_source_supplier.py`
`64cc1be4ab211787c1ace93de7520fed38d39f5ddc247a3fe783d682be2c9cdc`,
`_s2ty_evaluation.py`
`905507dd22f883f822546e95103cdd8063d0b9c85ca2ff9125c07edfd348357d`.

Gebundene Testhashes: `87cf65cbc31584549fb7607ce9e957b6330f2cf31d858332d9a3706fbfd2a11f`,
`9fd5f130c4777c160d06a738098f3420f0539248dad1d4faf47180196cf7e97d`,
`23d15d92e179d2bd4aac216a0a6fdc3ed06e432c607b715362a3b8f392ef98c3`,
`0328d2b5860530e9d7de32c1b63acf9d1eecc3f91e14b0dd2d9258bed5cd8332`.

Die historische `49/49`-Qualifikation bleibt als Abhängigkeit erhalten und
wird nicht wiederholt. Kennung `...-01` bleibt Entwicklungsprüfung vor der
ergänzten Vorbilanzprüfung und ersetzt diese Qualifikation nicht.
