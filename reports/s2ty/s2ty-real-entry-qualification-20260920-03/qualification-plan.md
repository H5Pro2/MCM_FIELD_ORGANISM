# S2-TY Real Entry: Abschlussbilanz-Qualifikation

Kennung: `s2ty-real-entry-qualification-20260920-03`. Erwartet werden 28
neutrale Tests aus `tests.test_s2ty_real_source_supplier`,
`tests.test_s2ty_evaluation`, `tests.test_s2ty_run_envelope` und
`tests.test_s2ty_real_run_entry`.

Zusätzlich zur Quellenbindung und äußeren Verifikationssperre prüft dieser
Bestand tatsächliche Abschlussgrößen, eine absichtlich zu kleine
Erfolgspublikationsreserve, begrenzte Fehlerhüllen nach Lieferanten-
Initialisierung und Auswertungsfehlern sowie Gate-Rücksetzung. Alle Quellen
sind neutrale In-Memory-Fixtures; keine NU-/TW-Payload wird erzeugt oder
analysiert.

Gebundene Hashes: `_s2ty_real_run_entry.py`
`9ae330743d072fb516ba9b1e223d9b7fa3f7b15a7a22c983de8a0bc6d5b1cac2`,
`_s2ty_run_envelope.py`
`151f4f08c2141bd0ffb3b69e183a3a8bb20bbd32acc863b48cc0da016347866b`,
`_s2ty_real_source_supplier.py`
`64cc1be4ab211787c1ace93de7520fed38d39f5ddc247a3fe783d682be2c9cdc`,
`_s2ty_evaluation.py`
`905507dd22f883f822546e95103cdd8063d0b9c85ca2ff9125c07edfd348357d`.

Gebundene Testhashes: `cd23857d9fbb7383cb37d758597b2c4f6c07a5ababe20cb2aad483da36c635d0`,
`9fd5f130c4777c160d06a738098f3420f0539248dad1d4faf47180196cf7e97d`,
`23d15d92e179d2bd4aac216a0a6fdc3ed06e432c607b715362a3b8f392ef98c3`,
`0328d2b5860530e9d7de32c1b63acf9d1eecc3f91e14b0dd2d9258bed5cd8332`.

Die historische 49er-Qualifikation bleibt erforderliche Abhängigkeit und
wird nicht wiederholt. Die Kennungen `...-01` und `...-02` bleiben erhalten
und ersetzen die neue Abschlussbilanzqualifikation nicht.
