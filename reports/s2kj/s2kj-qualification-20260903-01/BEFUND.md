# S2-KJ Qualifikationsbefund

## Status

`QUALIFICATION_FAILED_FIXTURE_TIME_BINDING`

Die private Binder- und Projektionsimplementierung wurde statisch erfolgreich
geprueft. Der einzige vorregistrierte Qualifikationsaufruf endete jedoch im
neutralen `setUpClass`, bevor einer der zwoelf Testkoerper lief.

## Einmalaufruf

```text
python -m unittest tests.test_s2kj_two_area_perceptual_context_336 -v
Exit-Code: 1
Ausgefuehrte Testkoerper: 0/12
Terminal: FAILED (errors=1)
```

Der zweite neutrale Formation-Schritt wurde durch die bestehende
TSPM-1-Zeitvalidierung als stale beziehungsweise geaenderter Quellclock
abgewiesen. Die Fixture erzeugt derzeit fuer jeden AV-Block einen neuen
`BroadbandHearingPath`; dadurch beginnt die interne auditive Quellzeit erneut,
obwohl die aeussere Common-Field-Zeit fortschreitet.

Dies ist ein Fehler der neutralen Testvorbereitung. Es liegt weder ein
S2-KJ-Funktionsbefund noch ein Memorybefund vor. Es wurde kein zweiter Testlauf
ausgefuehrt und keine nachtraegliche Fixturekorrektur vorgenommen.

## Statischer Preflight

- Python-Syntax: bestanden fuer beide Produktmodule und die Testdatei.
- Aktive Testliste: exakt zwoelf Testmethoden.
- Verbotene Produktimporte fuer Runner, Recorder, Plattform und Feld: keine.
- `git diff --check`: bestanden.
- S2-KI-Vertragsdigest: `2b350c0117b73c3367c8bad1f8f555e59e1170377beb539c41bb6e2df4b4de81`.

## Gebundene Quellhashes

| Datei | SHA-256 |
| --- | --- |
| `tools/_s2kj_validated_perceptual_finding_336.py` | `9e6a98181d1ccb5a32b8598493c09dd3eb5a67aa2ee355a4d71f1ee295123b85` |
| `tools/_s2kj_two_area_perceptual_context_336.py` | `5e2510eb6dd58ffef27901fc545ad700d1f8a5e4d5b3363d09811fe11c0a1d17` |
| `tests/test_s2kj_two_area_perceptual_context_336.py` | `8a794664ac8bc68aa6faee5fc06af3f1c6cd2942fb10cf070889d8d18c5eec1f` |

Die Hashes waren nach dem Lauf unveraendert.

## Grenze

`PRIVATE_TWO_AREA_PERCEPTUAL_CONTEXT_336_VALID` wird nicht gesetzt. Ein realer
Kontextnutzentest bleibt gesperrt. Fuer eine neue Qualifikation muss die
neutrale Audiofixture unter neuer Qualifikations-ID eine durchgehend streng
fortschreitende Quellzeit verwenden. Historische S2-KG-Belege bleiben
unveraendert und werden weder ergaenzt noch neu interpretiert.
