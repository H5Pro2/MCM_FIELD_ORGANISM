# S2-NS: neutrale Quellenbindungsqualifikation

Status: `S2NS_SOURCE_BINDING_QUALIFIED`, 14/14, Exit-Code `0`.
ID: `s2ns-source-binding-qualification-20260908-01`.

Genau ein vorregistrierter Testaufruf, kein Retry:

```powershell
C:/Python314/python.exe -m reports.s2ns.qualify_once
```

Der Einstieg rief genau einmal `python -m unittest
tests.test_s2ns_private_source_binding -v -f` aus dem workspace-Root auf.
Inventar, konkrete Grenzen, Umgebung und Quellhashes stehen vor dem Aufruf in
`preregistration.json`; das unveraenderte Testprotokoll steht in `stderr.txt`.
Alle 14 Pruefgruppen wurden erreicht. Die Vor-/Nachhashes sind identisch.

## Gepruefter Umfang

- Literale Quellen-, Rezept-, Ereignis-, Profil- und Zeitmetadaten;
  getrennte Quellenidentitaeten der vorgesehenen Exaktkopien.
- a06: zwei geordnete Dreiergruppen einschliesslich Nullamplituden und
  unveraenderter Phasenpositionen. Eine neutrale Zwei-Gruppen-Fixture mit
  16 Samples prueft exakte Float32-Bytes und alle 96 Sinusargumente gegen
  eine unabhaengige Referenz. Keine Nullposition wird uebersprungen.
- Ein neutraler 1920x1080-RGB-Frame: Raster, Kanaele und Bitreihenfolge.
- Komplementaere Sichten, alle 31 Ereignismetadaten, drei Geschichten,
  direkte Audioendpunktzeiten und getrennte Evaluationswurzel.
- Unveraenderlichkeit, manipulierte Bindungen, Built-in-math-Herkunft,
  exklusive Publikation, konkrete Metadatengroessen und geschlossene Gates.

NS-Rezeptmetadaten wurden mit synthetischen Payloadhashes geprueft.
NS-Payloads: `0`; Rezeptor-, NJ-, Distanz-, Memory-, Feld-, Kontext- und
Runtimeaufrufe: `0`. Keine historische Qualifikation wiederholt.

## Bindungen und Grenzen

Ergebnisdigest:
`86f0617b887de7abd191a57e3d69d322af40e570a1a9e0c6143a0dffa4e8dbd3`.

SHA-256 der unveraendert qualifizierten eigenen Dateien:

| Datei | SHA-256 |
| --- | --- |
| tools/_s2ns_private_source_binding.py | `9fae377019e832434166832b28f52acbbdd48d4cab97196cbb7b0a3d11d2a8a2` |
| tools/_s2ns_private_preseal_verification.py | `82b7f4697f8a2e75bd7a7e5b8312b7449ec47051fa2eac87b8b7042b1a58c2e2` |
| tests/test_s2ns_private_source_binding.py | `2458bf23b670b2eea3a0b6b194bcd262556daa04d2d9c19c8b6803d3a35be0d4` |
| reports/s2ns/qualify_once.py | `ebde6e0a316d1a5902c9e554a1c83724c48f88a73f8bed915faf3e5198a02342` |
| reports/s2ns/preseal_once.py | `3db94aa11fb955ef9cb18b746f298d1762998422e4d2cf2f082109949ea6bbf7` |
| reports/s2ns/QUALIFIKATIONSBINDUNG.md | `1e6835ca6db5d50ddd735188aed15a2ebf875c718e3b9738ad01805bd188ae1a` |

Der vollstaendige Hashsatz einschliesslich historischer Abhaengigkeiten ist
in `result.json` enthalten. Die Qualifikation traegt nur die rezeptorfreie
Quellenanbindung. Sie bestaetigt keine Rezeptornormalform, Treffermengen,
Zulassung oder Zwei-Sichten-Implementierung. Hauptgates bleiben `False`.

WEITER: Am besten geht es jetzt mit der Analystenpruefung der separat
aufgezeichneten einmaligen Vorversiegelung weiter.
