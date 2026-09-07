# S2-NP: neutrale Neuqualifikation nach enger Testkorrektur

## Ergebnis

Lauf-ID: `s2np-coverage-comparison-qualification-20260907-02`.
**S2NP_COVERAGE_COMPARISON_QUALIFIED**, **22/22 bestanden**, Exit-Code **0**.
Genau ein vollstaendiger Qualifikationsaufruf, ein unittest-Unterprozess,
kein Retry. Testinventar, Budget, Interpreter- und Quellhashes wurden vor
dem Unteraufruf in `preregistration.json` gebunden.

Kommando aus dem workspace-Root:

```powershell
C:/Python314/python.exe -m reports.s2np.qualify_coverage_once
```

Gebundener Unteraufruf:

```powershell
C:/Python314/python.exe -m unittest tests.test_s2np_private_coverage_comparison -v
```

## Ausschliessliche Korrektur

In Testgruppe 22 wird zuerst eine feste gueltige synthetische Nullwert-Fixture
mit Quellen-ID `np-a03` gebunden. Deren gueltige Herkunftsmetadaten werden
unveraendert fuer die drei unabhaengigen numerischen Unterfaelle verwendet.
Erst der Produkteinstieg `project_values` erhaelt jeweils `Inf`, `-0.01`
oder `1.01` als Werte. Kein JSON-Digest wird aus `Inf` erzeugt.

Jeder Unterfall besitzt einen eigenen `subTest`-Block und prueft sowohl
die konkrete Klasse `S2NPCoverageError` als auch exakt die Ausnahmeargumente
`("VALUE_DOMAIN_INVALID",)`. Keine allgemeine ValueError-/Exception-Akzeptanz.
Alle bisherigen 22 Testgruppen einschliesslich der Subnormal- und
numerischen Termkontrollen bleiben erhalten.

Ausserhalb der Teststelle wurde nur die Qualifikations-ID von `...-01` auf
`...-02` geaendert. Produktmodule, `allow_nan=False`, Vergleichsregeln,
Masken, Quellen, Profile und Grenzen blieben unveraendert. Der erste
Fehlbeleg bleibt dauerhaft `NOT_QUALIFIED` und wurde nicht ueberschrieben.

## Umfang und Grenzen

- 8736 synthetische Banddifferenzen im gesamten neutralen Testaufruf;
  vorgebundene Qualifikationsobergrenze 16384.
- Darin ein vollstaendiges synthetisches Inventar je Implementierung:
  je 360 Panelbefunde, 360 regelgebundene Beziehungszeilen und 3840
  Banddifferenzen. Das spaetere Korpuslimit bleibt insgesamt 7680.
- Konkrete kanonische Test-Gesamtausgabe: 1112286 Byte bei Grenze 2097152,
  einschliesslich der bereits gebundenen Materialisat-/Metadatenreserven.
  Kein universeller Worst-case- oder Prozesspeaknachweis.
- Reale NP-Rezeptorwerte nicht geladen oder verglichen. Historische
  Materialisierungsdateien ausschliesslich fuer Dateihashes gelesen.
- Payloadgeneration, Rezeptor-, NJ-, Memory-, Feld-, Kontext- und
  Runtimeaufrufe jeweils 0. Gates bleiben `False`.

Die Qualifikation bestaetigt die gepruefte technische Vergleichsanbindung,
nicht einen Abdeckungsvorteil oder eine Erhaltung auf dem realen NP-Korpus.
Die einmalige reale Vergleichsauswertung bleibt separat freizugeben.

## Bindungsbelege

Alle vor/nach dem Aufruf gebundenen Quellhashes stimmen ueberein.
Die drei Produktmodule stimmen ausserdem mit der ersten Qualifikation ueberein:

| Datei | SHA-256 |
| --- | --- |
| Vergleich | `3b8824de8d0ca391a8312d803896544029b2dcbfdfa39e21f7190f81d719ecd8` |
| Direktbaseline | `2bb83762ff674a26e9df4f36bd5154fff0a15e1dfa20c13f15fc33867d91c495` |
| Auswerter | `50e4766c2b6f6bec4ba926767a82a18039ffd73046a0a9626c813f75f462b2a9` |
| Korrigierte Testdatei | `ae66d4d55875e7e91027d47a880e0c9f87c570e39dfc4a77cadb606fb241805a` |
| Qualifikationsaufrufbindung | `a579613bc7524f9f1b571c82e537846736e9fb54781ce811437daafabc833de5` |

Vorregistrierungsdatei SHA-256:
`ded8acf1512286217e0ee961bef13bb12c1fdc55da63d19e492d57944fc0236a`.

Ergebnisdatei SHA-256:
`3ffca698756fb33a2a16f854ec5f61b31dbab0bc8983c85e2b13b4e899e4f983`.

Kanonischer Ergebnisdigest:
`6c104e8afb5456cda6f8c20cdd181c33ff94c0c8bbacac01f02e3f70a9367f9d`.

Vollstaendige Bindungen und Testprotokolle stehen in `preregistration.json`,
`result.json`, `stdout.txt` und `stderr.txt`. Keine erneute Test- oder
numerische Verifikationsausfuehrung nach diesem Aufruf.
Historische Belege, fremde Aenderungen und Bootstrap bleiben unberuehrt.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser bestandenen
Neuqualifikation und der separaten Entscheidung ueber die einmalige reale
NP-Vergleichsauswertung weiter.
