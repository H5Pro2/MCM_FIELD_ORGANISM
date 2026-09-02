# S2-JX - Default-Live-Memory-Funktionsbefund

## Status

`S2JX_FUNCTION_CONFIRMED`

Der einmalige private Funktionslauf bestaetigt fuer die gebundene synthetische
Default-Live-Fixture eine audiovisuelle Zwei-Bereich-Memory mit `48 + 288 =
336` echten Rezeptorwerten. Der Befund gilt ausschliesslich fuer die
vorregistrierte Folge und ihre mechanischen Schwellen. Er ist kein Nachweis
allgemeiner Langzeit-Memory, semantischen Lernens oder einer validierten
Wahrnehmungsaehnlichkeit im Default-Live-Profil.

## Implementierte Laufgrenze

- `tools/_s2jx_default_live_memory_fixtures.py` erzeugt die elf gebundenen
  RGB8-/PCM-Fixtures streaming und prueft Roh- sowie Rezeptorwertedigests;
- `tools/_s2jx_default_live_memory_runner.py` orchestriert exakt 15 atomare
  Formationen und drei read-only Proben;
- `tools/_s2jx_default_live_memory_result_verifier.py` prueft die atomare
  Ergebnisdatei ohne Rezeptor- oder Memoryaufruf;
- `tests/test_s2jx_default_live_memory_runner_qualification.py` qualifiziert
  Gate, neutralen realen Adapterpfad, Operationskette, atomare Speicherung,
  Falsifikationsgrenze und Manipulationserkennung.

RGB- und PCM-Rohdaten werden jeweils nur fuer die aktuelle Rezeptorreduktion
gehalten. Die Ergebnisdatei enthaelt keine Rohpayloads, keinen Feldsnapshot,
keine Kontextwahl und keine 336-zu-26-Kompression.

## Neutrale Qualifikation

Qualifikations-ID: `s2jx-runner-qualification-20260902-01`

Einziger Testaufruf:

```text
python -m unittest tests.test_s2jx_default_live_memory_runner_qualification -v
```

Ergebnis:

```text
Ran 12 tests in 0.465s

OK
Exit-Code: 0
```

Die vier Qualifikationsquellen hatten vor und nach dem Lauf identische
SHA-256-Digests:

| Quelle | SHA-256 |
| --- | --- |
| Fixture | `5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936` |
| Runner | `4a59b92a2b3b3e482b8934061b2592aa2503293d313151f90a799f018f58ef51` |
| Verifikator | `d5bcf53f5d956262d1a3f0ff58e69e4e4d6470adafc176a4d8383b22809f5a54` |
| Test | `5dffee0bc4ae8d16f90e43ee2b95ea3a285bb7f4f2415d67202c2a600d897701` |

## Einmaliger Funktionslauf

Lauf-ID: `s2jx-default-live-memory-20260902-01`

Gebildete Folge:

```text
X X X X Y Y D1 D2 D3 D4 D5 D6 D7 D8 D9
```

Read-only Proben:

```text
D9 X Y
```

Gebundener Umfang und tatsaechlicher Belegumfang stimmen ueberein:

| Position | Wert |
| --- | ---: |
| Formationen | 15 |
| Proben | 3 |
| Top-Level-Memoryoperationen | 72 |
| L1-Terme | 43.680 |
| gespeicherte Ergebnisbytes | 86.966 |

Die atomare Ergebnisdatei besitzt SHA-256
`0ed7b62c873603feefde3e5cf4ed949cfc1323ff36e0adc22d58a4ccc8a92547`
und den internen Recorddigest
`d3cc6abd714bcba9c06fec4ff14722fe239394f3cae0979a7c94bdf9d283af35`.

## Read-only Verifikation

Der Verifikator wurde nach der vollstaendigen Aufzeichnung genau einmal
aufgerufen. Ergebnis:

```text
VERIFICATION_STATUS=RECORDING_COMPLETE
FUNCTIONAL_STATUS=S2JX_FUNCTION_CONFIRMED
OPERATION_COUNT=72
ISSUES=[]
VERIFICATION_DIGEST=e9c4bc3bda863805efd4111f3a333273f895a58160ca6f5bedbffa91a1f63314
Exit-Code: 0
```

## Funktionsergebnis

| Probe | B4_RECENT | TSPM_FAST | Slow auditiv | Slow visuell |
| --- | --- | --- | --- | --- |
| D9 | Treffer, Formation 15 | Support 1 | kein stabiler Treffer | kein stabiler Treffer |
| X | kein Treffer | kein Treffer | Treffer, Support 3 | Treffer, Support 3 |
| Y | kein Treffer | kein Treffer | kein oeffentlicher Treffer | kein oeffentlicher Treffer |

Y bleibt intern in beiden PPB-Banken als instabile Spur mit Support `1`
sichtbar. Diese Spur ist nicht stabil und erzeugt deshalb keinen oeffentlichen
Slow-Treffer. Das ist kontrolliertes funktionales Vergessen im gebundenen
Zwei-Bereich-Modell, keine Behauptung physischer Zustandsloeschung.

Alle drei Probezugriffe hielten Vor- und Nachzustandsdigest identisch. Der
gemeinsame Endzustandsdigest lautet
`1e62a53b6a6721af59f554428ed72154292769c87380fb6970f5718c759a766e`.

## Aussagegrenze

Bestanden ist genau die Frage, ob der bestehende unveraenderte B4-/TSPM-/PPB-
Verbund mit real erzeugten 336-Werte-Rezeptorzustaenden gleichzeitig D9 als
juengsten Inhalt, X als wiederholungsbedingt stabilen Inhalt und Y als zu
schwach verdichteten, nicht mehr oeffentlich abrufbaren Inhalt abbildet.

Nicht untersucht wurden Feldrueckwirkung, Kontextwahl, Semantik,
Langzeitstabilitaet, allgemeine Aehnlichkeitskalibrierung oder reale zweite
Audio-/Videoquelle.
