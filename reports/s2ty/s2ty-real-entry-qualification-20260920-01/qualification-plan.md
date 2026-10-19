# S2-TY Real Entry: neutrale Anschlussqualifikation

Kennung: `s2ty-real-entry-qualification-20260920-01`.
Vor dem einzigen Aufruf gebunden sind die Testmodule
`tests.test_s2ty_real_source_supplier`, `tests.test_s2ty_evaluation`,
`tests.test_s2ty_run_envelope` und `tests.test_s2ty_real_run_entry`.
Erwartet werden 25 Tests. Der Aufruf verwendet nur neutrale In-Memory-PCM-
Fenster, einen ersetzten Quellenlieferanten und temporäre Ausgabeordner.

Geprüft werden Lazy-Quellenbindung, native `bytearray`-Übergabe, 22 direkte
Hash-/Rezeptor-/NJ-Aufrufe im neutralen Erfolgsfall, Abbruch nach dem dritten
Lieferantenzugriff, vorhandene Ausgabe, Gate-Rücksetzung, äußere
Verifikationssperre, einmalige Veröffentlichung und die Auswertung nach
äußerer Verifikation. Keine NU-/TW-Payload wird erzeugt oder verarbeitet.

Gebundene Codehashes: `_s2ty_real_run_entry.py`
`94728d9ad1b19a990d3d8380a15846ce6454ad3fc1ef80551a7e56b0a3e2e4f1`,
`_s2ty_run_envelope.py`
`151f4f08c2141bd0ffb3b69e183a3a8bb20bbd32acc863b48cc0da016347866b`,
`_s2ty_real_source_supplier.py`
`64cc1be4ab211787c1ace93de7520fed38d39f5ddc247a3fe783d682be2c9cdc`,
`_s2ty_evaluation.py`
`905507dd22f883f822546e95103cdd8063d0b9c85ca2ff9125c07edfd348357d`.
Die Testhashes sind `23d15d92e179d2bd4aac216a0a6fdc3ed06e432c607b715362a3b8f392ef98c3`,
`0328d2b5860530e9d7de32c1b63acf9d1eecc3f91e14b0dd2d9258bed5cd8332`,
`9fd5f130c4777c160d06a738098f3420f0539248dad1d4faf47180196cf7e97d`
und `60e990b68f7f5bc3cb0e6628ea89bb7476b4cc652cc9ffe66be7e6e15a9c2743`.

Die vorherige 49er-Qualifikation wird nicht wiederholt. Ihr Ergebnis
`dce17b722f70ab1cb9cb80891cb79d55058eec21144026338bde13826d7c4066`
bleibt eine erforderliche, historische Abhängigkeit.
