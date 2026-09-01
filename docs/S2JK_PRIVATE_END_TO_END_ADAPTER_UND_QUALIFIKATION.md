# S2-JK - Privater End-to-End-Adapter und Qualifikation

## Status

`PRIVATE_END_TO_END_ADMITTED_CONTEXT_USE_VALID`

Qualifikations-ID:

`s2jk-end-to-end-context-use-qualification-20260901-01`

S2-JK implementiert den begrenzten privaten Pfad von einer bereits
qualifizierten S2-IC-Kontextbeurteilung und S2-JH-Zulassung zur spaeteren
maskierten Folgewahrnehmung. Es wurde keine Memory-, Rezeptor-, Feld-,
Runner-, Recorder-, Registry- oder Plattformfunktion hinzugefuegt.

## Implementierung

| Rolle | Datei | SHA-256 vor und nach dem Lauf |
| --- | --- | --- |
| End-to-End-Adapter | `tools/_s2jk_private_end_to_end_context_use.py` | `21eefd13fba247b678a9d23afee4a47fc813852c82dae6901da81f97eb39713b` |
| Unabhaengige direkte Komposition | `tools/_s2jk_private_direct_end_to_end_baseline.py` | `2178fc6a1e652370290f789f13286d8490719db240b7b894f7c3553ea1246fa4` |
| Neutrale Vertragstests | `tests/test_s2jk_private_end_to_end_context_use.py` | `d93ffdb4be7e6d15c1190c2d5b9f32e91e59d2f793cdbe6f8109ac52ed9a0ffd` |

Der Adapter berechnet weder Status noch Anwendbarkeit neu. Er prueft die
bereits vorhandenen Quellen-, Receipt-, Owner-, Zustands- und
Zulassungsbindungen relational und verwendet ausschliesslich vorhandene
maskierte Ergaenzungswerte.

- `SINGLE_SOURCE`: genau die zugelassene A- oder B-Rolle wird verwendet.
- `CONSISTENT`: nur die digestgleich gebundene gemeinsame Ergaenzung wird
  ohne Rollenpraeferenz materialisiert.
- `CONFLICT`, `NO_CONTEXT`, `NO_APPLICABLE_CONTEXT`: die Probe bleibt
  unveraendert; die Fuellfunktion wird nicht aufgerufen.

Die unabhaengige Baseline besitzt eine eigene literale Entscheidungstabelle,
eigene Bindungspruefungen fuer Einzelquelle und Gleichwertigkeit sowie eine
eigene direkte Maskenfuellung. Sie ruft weder den Adapter noch dessen
funktionale Zwischen- oder Ergebnisbildung auf.

## Qualifikationsbefund

Vor dem Lauf bestanden Syntax-, Import-, Quellen- und Testanzahlpruefung.
Danach wurde genau ein Testaufruf ausgefuehrt:

```text
python -m unittest tests.test_s2jk_private_end_to_end_context_use -v
Ran 12 tests in 0.158s
OK
Exit-Code 0
```

Geprueft wurden:

- alle fuenf Statuswerte;
- A/B-Spiegelung bei `SINGLE_SOURCE`;
- `CONSISTENT` ohne Listen- oder Rollenpraeferenz;
- kein Fuellaufruf bei allen drei Enthaltungsstatus;
- unveraenderte sichtbare Werte und genau neun Maskenuebernahmen;
- manipulierte, vertauschte und fremde Zulassungs- oder Quellenbelege;
- Gleichheit mit der unabhaengigen Direktbaseline;
- unveraenderte Probe-, Bundle-, Signal-, Zulassungs- und Zustandsdigests;
- Null Memory-, Rezeptor- und Feldaufrufe sowie endliche Artefaktgrenzen.

Die drei Quellhashes waren vor und nach dem Lauf identisch.

## Aussagegrenze

Der Befund qualifiziert ausschliesslich die private kontrollierte Verwendung
eines bereits zugelassenen Kontextes. Er ist kein realer Acht-Faelle-Lauf,
keine automatische Kontextauswahl, kein Lernbefund und keine Feldwirkung.
Die direkte Tabellen- und Fuellbaseline erklaert die Funktion vollstaendig.

Der reale Acht-Faelle-Lauf ueber die vorhandene Laufhuelle bleibt bis zu einer
separaten Freigabe gesperrt. Danach wird der Kontextzweig unabhaengig vom
Ergebnis geschlossen; die quellenunabhaengige Pixel-/Audio-Grenze bleibt der
naechste Hauptabschnitt.
