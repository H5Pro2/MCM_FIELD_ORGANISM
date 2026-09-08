# S2-NR: neutrale Quellenbindungsqualifikation

2026-09-08. Lauf-ID: s2nr-source-binding-qualification-20260908-01.
Ausgangscommit c4c848b. Genau ein Aufruf, kein Retry:

```text
C:/Python314/python.exe -m reports.s2nr.qualify_once
```

Der einmalige Unterprozess war:

```text
C:/Python314/python.exe -m unittest tests.test_s2nr_private_source_binding -v -f
```

Exit-Code 0, 12/12, Ran 12 tests in 0.130s, OK.
Status S2NR_SOURCE_BINDING_QUALIFIED. Testinventar, Budget und alle sechs
eigenen Datei- sowie historischen Quellhashes waren vorab in
[preregistration.json](preregistration.json) gebunden. Alle beobachteten
Quellhashes vor/nach dem Aufruf identisch. Vollstaendiges Originalprotokoll:
[stderr.txt](stderr.txt); stdout.txt ist die unveraenderte leere Ausgabe.

Geprueft: literale Quellenidentitaeten und Exaktkopien, unveraenderliche
Spezifikationen, Partial-/Float32-Reihenfolge, RGB-Bit-/Rastergeometrie,
18 Ereignisse und Quellenvorkommen, native und gemeinsame Zeitfenster,
Masken/Komplemente, Profilmetadaten, getrennte Planwurzeln, unabhaengige
Manipulationsfaelle, Built-in-math-Bindung, exklusive Publikation,
Uebergroesse und Ausschluss von Systemimports.

Nur eine neutrale PCM-Quelle mit 16 Samples/64 Byte und ein neutrales
RGB-Vollbild mit eigenem Seed/6.220.800 Byte wurden erzeugt. Die skalare
PCM-Referenz bildet dieselbe neutrale Bytefolge unabhaengig nach.
NR-Rezepte wurden nur als Metadaten mit synthetischen Payloadhashes geprueft.
Keine NR-Payloads, Rezeptoren, NJ, Kontakte, Distanzen, Memory, Kontext,
Feld oder Runtime. MAIN_GATE blieb False.

Resultdigest:
`02f11db013890fbfaa09d79832bc971961d9c716093b56215a1c68aef75cff74`.
result.json-Dateihash:
`066904c2ff12feb36c71e4d05de6314e8bef557ea0897c4a0ed30f18d4954290`.
preregistration.json-Dateihash:
`010e6ef65c3fbf6af6bd3bafdcd9ae560d406495078741c86d9afbea338acab3`.
stderr.txt-Dateihash:
`71ce775e850d41115f580db5c8bbede62bb76fdb4ac4752f600242e5988cd73f`.

Eigene qualifizierte Dateien, SHA-256:

| Datei | SHA-256 |
| --- | --- |
| tools/_s2nr_private_source_binding.py | c0e748e2e6cdc24f3c084b3690eafe1fc6bbec036e61c663b9323595fe80c824 |
| tools/_s2nr_private_preseal_verification.py | dd14675a8dbe6a1d101a35ffc9b16ffa0f9d429894d567a13c63320bc5bc5127 |
| tests/test_s2nr_private_source_binding.py | ac88a25a40ba8f72c7bf3ead160ff8a9ff78e8d61b7e7c126f0ff158e78dea94 |
| reports/s2nr/qualify_once.py | 0ac9a5a082d2ef313741f8be4db2a9d8cdf1c63afb1b35eb36aaf70f943682b3 |
| reports/s2nr/preseal_once.py | 89c108a96a31ec0887cb2fcfa4b7cafdd58f1d2c308cee5e5466168cf24f2f9d |
| reports/s2nr/QUALIFIKATIONSBINDUNG.md | 9666a1089d4d2250fb9dbfb9cf23e88ee497779f231eda8420850fa66161087f |

Dies qualifiziert die kleine rezeptorfreie NR-Bindung, nicht den geplanten
Cue-/Hypothesenanschluss oder irgendeine Rezeptor-/Memoryfunktion.
Die anschliessende, getrennte einmalige Quellenversiegelung ist im
[Vorversiegelungsbefund](../s2nr-source-preseal-20260908-01/BEFUND.md) belegt.
