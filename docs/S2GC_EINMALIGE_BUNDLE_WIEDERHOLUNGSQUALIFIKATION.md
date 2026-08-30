# S2-GC: Einmalige Bundle-Wiederholungsqualifikation

## Laufbindung

Qualifikations-ID:

`s2gc-bundle-qualification-20260830-01`

Vor dem Lauf wurde statisch bestaetigt:

- genau zwoelf Testdefinitionen;
- ausschliesslich die zwei in S2-GB festgestellten Fixture-Aufrufe 08 und 09
  verwenden die korrigierte leere Sequenzevidenz `available=False`;
- Bundleimplementierung und die uebrigen zehn Tests entsprechen dem
  versionierten S2-GB-Stand;
- der erste Lauf bleibt als `QUALIFICATION_FAILED_FIXTURE_ERROR` erhalten.

## Quellbindung

| Quelle | SHA-256 vor Ausfuehrung | SHA-256 nach Ausfuehrung |
| --- | --- | --- |
| `tools/_s2gb_private_perceptual_context_bundle.py` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| `tests/test_s2gb_private_perceptual_context_bundle.py` | `a557defc4a5309b86b3f9b7d56d78c3db3e61784b67706335cc3922a9519e55e` | `a557defc4a5309b86b3f9b7d56d78c3db3e61784b67706335cc3922a9519e55e` |

Die Quellhashes blieben waehrend der Qualifikation unveraendert.

## Einmalige Ausfuehrung

Es erfolgte genau ein Aufruf:

```text
python -m unittest tests.test_s2gb_private_perceptual_context_bundle -v
```

Terminaler Befund:

```text
Ran 12 tests in 0.015s

OK
EXIT_CODE=0
SOURCE_HASHES_UNCHANGED=True
```

Alle zwoelf vorab gebundenen Faelle bestanden. Es gab keine Wiederholung,
Nachkorrektur oder Aenderung der Quellen im Laufschritt.

## Entscheidung und Grenze

Die Bedingungen `12/12`, Exit-Code `0` und terminales `OK` sind gemeinsam
erfuellt. Der technische Status lautet deshalb:

`PRIVATE_READ_ONLY_PERCEPTUAL_CONTEXT_BUNDLE_VALID`

Dieser Status bestaetigt ausschliesslich die private, unveraenderliche,
digestgebundene und fail-closed Bundleprojektion. Er belegt noch keine
funktionale Kontextverwendung. Automatische Auswahl, Feldrueckwirkung, API,
Snapshot, Produktionsintegration und Lernoperation bleiben gesperrt.
