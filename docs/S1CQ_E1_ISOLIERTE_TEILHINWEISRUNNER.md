# S1-CQ: E1 isolierte Teilhinweisrunner

## Status

Die isolierten Cue-Runner fuer E1, P0 und den einen statischen H8-Adapter
sind implementiert und technisch abgenommen. Einzelne Arme wurden geprueft;
die vollstaendige 36er-Matrix wurde nicht gebildet und keine
Forschungsentscheidung wurde erzeugt.

## Implementierung

```text
mcm_field_organism/e1_partial_cue_runners.py
tests/test_e1_partial_cue_runners.py
```

Die Rollen bleiben privat.

## Runnerkontext

Der Kontext enthaelt:

- die drei S1-CP-Zustaende `left-g4`, `right-g4`, `neutral`;
- genau einen festen Kantenratenadapter aus der linken H8-Geschichte.

Der B1-Adapter wird nicht pro Geschichte oder Hinweis neu bestimmt. E1
berechnet seinen festen Adapter aus dem jeweils injizierten G4-Zustand. P0
verwendet keinen langsamen Adapter.

## Isolierter Ablauf

Jede Beobachtung startet fuer n=2 und n=4 von getrennten frischen
Drei-Knoten-Feldkopien. Derselbe Hinweis wird parallel mit P0 und dem
gewaehlten Adapter ausgefuehrt. Berichtet wird nur deren signierte S/H-
Differenz. Kein langsamer Zustand wird waehrend des Hinweises fortgeschrieben.

```text
Hinweisdauer: 1.0 s
Rate:         20 Hz
n=2:         2 * 10 Ticks
n=4:         4 * 5 Ticks
```

## Isolierte Abnahmebefunde

```text
E1 left-g4 / left-partial L-inf: 0.0006520385767639081
E1 left-g4 / left-full    L-inf: 0.0026081543070556323
P0 neutral / left-partial L-inf: 0.0
B1 left-g4 / left-partial L-inf: 0.0017386506934377322
maximaler hier berichteter relativer n=2/n=4-Rest: 7.023618141288273e-13
```

Der isolierte E1-Viertelhinweis ist in diesem Arm exakt proportional zur
Vollhinweisgroesse. Das ist erwartete lineare Feldantwort und weder
Mustervervollstaendigung noch Rekonstruktion. P0 ist exakt null. B1 liefert
einen technischen Effekt, bleibt aber fuer denselben Hinweis ueber
`left-g4`, `right-g4` und `neutral` wertgleich und besitzt daher keine
Historyinteraktion.

Die passenden linken und rechten E1-Arme sind bis `1e-12` gespiegelt.
Eingangsfeld, G4-Zustaende und fester H8-Adapter bleiben unveraendert.

## Technische Abnahme

Acht fokussierte Runnerpruefungen und 52 relevante Verbundtests bestehen.
Die abgeschlossenen Einmallaufartefakte wurden nicht veraendert und die
36er-Cue-Matrix wurde nicht zusammengesetzt.

## Aussagegrenze

S1-CQ zeigt nur, dass alle benoetigten Einzelbeobachtungen reproduzierbar
und kontrolliert erzeugt werden koennen. Die Messbarkeit eines einzelnen
E1-Arms ist kein history-spezifischer Effekt. Insbesondere folgt daraus kein
Rekonstruktions-, Memory-, Bedeutungs- oder KI-Befund.

## Bester naechster Schritt

S1-CR bindet die 36 isolierten Rollen als lazy, schreibgeschuetztes Inventar
mit festem Digest. Inventaraufbau darf keinen Cue-Runner, keinen Kompositor
und keine Entscheidung aufrufen. Erst danach kann ein getrennter
Einmallaufvertrag registriert werden.
