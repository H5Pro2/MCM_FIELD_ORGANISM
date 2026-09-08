# S2-NT: begrenzte rezeptorfreie Quellenqualifikation

Vorabbindung fuer genau einen Aufruf unter
`s2nt-source-binding-qualification-20260908-01`. Kein Retry.

16 Testkoerper in `tests/test_s2nt_private_source_binding.py`:
Inventar, Unveraenderlichkeit, Exaktidentitaeten, Gruppen/Nullpositionen,
native Fenster, ungueltige Starts, manipulierte Zeitbindung, vollstaendige
Paare, Ordnungsmetadaten, getrennte Wurzeln, neutrale Generatorarithmetik,
Quellenmanipulationen, Profile/Budgets, Publikationsgrenzen, unabhaengige
Metadatenpruefung/Kollisionen und math-/Importgrenze.

Einziger neutraler PCM-Aufruf: zwei Samples, zwei Gruppen zu je drei
Partialpositionen, acht Payloadbytes, zwoelf Sinusaufrufe. Die unabhaengige
neutrale Referenz benoetigt zwoelf weitere Sinusauswertungen. Keine NT-Payloads.
Native Zeiten und Tabellen werden ausschliesslich als Metadaten geprueft.
Keine Rezeptor-, NJ-, Distanz-, Memory-, Feld-, Kontext- oder Runtimeaufrufe.

Vor dem Test bindet `qualify_once.py` das vollstaendige AST-Testinventar,
Quellhashes, Befehl, Interpreterumgebung und diese Grenzen; danach Exit-Code,
Protokollhashes und unveraenderte Quellhashes. Ein Testfehler stoppt den Auftrag.

Nur bei Bestehen ist `s2nt-source-preseal-20260908-01` vorgesehen: einmal
14 PCM-Fenster, maximal ein Fenster von 19200 Byte gleichzeitig, insgesamt
268800 generierte Bytes ohne Rohablage. Historischer reiner NC-Generator
wird isoliert wiederverwendet, kein historischer Haupteinstieg ausgefuehrt.
Die anschliessende unabhaengige Pruefung liest nur Bindungen und Dateien,
keine erneute Payloadgenerierung. Zwei Planwurzeln, je hoechstens 65536 Byte;
Verifikationsbeleg maximal 262144 Byte. Alle Systemgates bleiben False.

Eine gueltige Vorversiegelung behauptet weder gueltige Rezeptorwerte noch
Trennleistung. Die spaetere Rezeptor-/NJ-Materialisierung und der Vergleich
bleiben separat freizugeben. Historische Artefakte bleiben unveraendert.
