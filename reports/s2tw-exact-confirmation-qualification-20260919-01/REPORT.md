# S2-TW-Neutralqualifikation 20260919-01

Status: `QUALIFIED`, `13/13`.

Die neutrale Prüfung verwendete ausschließlich synthetische 48-Wert-Vektoren;
keine S2-TW-Quelle wurde erzeugt oder materialisiert. Abgedeckt sind die
historisch unveränderte S2-TU-Regel, Vollgleichheit, FIFO-Alter bei
Bestätigung, Umkehrfolge, eine gezielte einzelne Werteabweichung, read-only
Hints, Quell- und Belegmanipulationen sowie die unabhängige Rekonstruktion
von Übergängen, Inventaren und Entscheidungen.

Die reale Hülle ist vor Start an höchstens `26` Ereignisse, `22`
Audioendpunkte, `16` Formationen, `10.752` native Vektorbytes über beide
Stores sowie die unveränderten Grenzen `98.304`/`65.536`/`262.144` Byte
gebunden. Die Einzelwertfixture ist nur eine Neutralprüfung; sie behauptet
nichts über die späteren Rezeptorwerte.

Aktive Dateien, SHA-256:

* `_s2tw_exact_confirmation.py`: `90470980a329d0424bec9ba430adbbccaf72bb82145edfefd6e491b6fcec7be9`
* `_s2tw_source_schedule.py`: `3e8f37ab8675da0a1f34bc14a6bd561fd111d48906728b4df99e5cd429c97cf4`
* `_s2tw_run.py`: `7e7d1564905bc0248ee239b38d2062557ff1530d13b44c0ff46535b4870444e4`
* `_s2tw_verification.py`: `56b93873c46f01c5c714178298ac02039daa7fd6174bc91ff2cdf24a406e3f41`
* `test_s2tw_exact_confirmation.py`: `db26a9456f02b1eee4c0d76db8527467380e6d82bc99d68f2f034e1ff28a30ae`
* `test_s2tw_schedule.py`: `b1ac8880966ad0c8207a4e2eaf0d8a5d34f0db350938a695d22bb276ccce5a55`
* `test_s2tw_verification.py`: `37f6426d4d07687a34fefc0fc5988fc9ca9cc2b94a674cc33b9625db73b4dfd7`

Die Quellenwurzel bleibt an
`6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`
gebunden. Feld, A/B-Memory und Hypothesen sind ausgeschlossen.
