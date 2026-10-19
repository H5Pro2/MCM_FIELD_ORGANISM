# S2-TY Real Entry: terminale Fehlerabschlussqualifikation

Kennung: `s2ty-real-entry-qualification-20260920-04`. Erwartet werden 30
neutrale Tests aus `tests.test_s2ty_real_source_supplier`,
`tests.test_s2ty_evaluation`, `tests.test_s2ty_run_envelope` und
`tests.test_s2ty_real_run_entry`.

Der Bestand prüft die vollständige Erfolgs- und Fehlerhülle sowie den
unabhängig reservierten Terminalbeleg. Für die gleichzeitige Überschreitung
beider vollständigen Publikationsreserven muss ausschließlich
`terminal-error.json` entstehen. Es bindet Größe und Digest nicht
publizierbarer Artefakte und markiert den Evidenzverlust ausdrücklich. Ein
Lieferanteninitialisierungsfehler und ein unerwarteter Ausführungsfehler
werden getrennt als `SUPPLIER_INITIALIZATION` beziehungsweise `RUN_EXECUTION`
mit unbekanntem Fortschritt geführt.

Alle Quellen sind neutrale In-Memory-Fixtures. Es gibt keine NU-/TW-Payload,
keinen Hauptlauf und keine reale Ergebnisablage.

Gebundene Hashes: `_s2ty_real_run_entry.py`
`905f272a466b27c4e75fa5e69bca9cb60aa97ed5f378b875b103345e1863fe11`,
`_s2ty_run_envelope.py`
`151f4f08c2141bd0ffb3b69e183a3a8bb20bbd32acc863b48cc0da016347866b`,
`_s2ty_real_source_supplier.py`
`64cc1be4ab211787c1ace93de7520fed38d39f5ddc247a3fe783d682be2c9cdc`,
`_s2ty_evaluation.py`
`905507dd22f883f822546e95103cdd8063d0b9c85ca2ff9125c07edfd348357d`.

Gebundene Testhashes: `e1ea621a1118e1700f469b10f53871ff1a4341b28e8f2d680dbf31434726862c`,
`9fd5f130c4777c160d06a738098f3420f0539248dad1d4faf47180196cf7e97d`,
`23d15d92e179d2bd4aac216a0a6fdc3ed06e432c607b715362a3b8f392ef98c3`,
`0328d2b5860530e9d7de32c1b63acf9d1eecc3f91e14b0dd2d9258bed5cd8332`.

Die historische 49er-Qualifikation bleibt erforderliche Abhängigkeit und
wird nicht wiederholt. Die Kennungen `...-01` bis `...-03` bleiben erhalten
und ersetzen die neue terminale Fehlerabschlussqualifikation nicht.
