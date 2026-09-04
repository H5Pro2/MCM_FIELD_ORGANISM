# S2-LR Rezeptorgeometriematerialisierung 2026-09-04-02

Status: `S2LR_VARIATION_GEOMETRY_NOT_MATERIALIZABLE`

Der einmalige Rezeptorlauf wurde ohne Memory-, Feld- oder Kontextaufruf
ausgefuehrt. Es gab keine Parametersuche, Nachjustierung oder Wiederholung.

## Entscheidender Befund

Die auditive Holdout-Gegenprognose ist mit der vorab gebundenen PCM-Fixture
nicht erfuellt:

- F: Holdout zu PLUS `0.019907943538015553`, zu MINUS
  `0.01990794361470144`;
- G: Holdout zu PLUS `0.019796552537115257`, zu MINUS
  `0.019737506748451653`;
- aktive Slow-Schwelle: `0.02`.

Die Holdouts liegen damit nicht ausserhalb aller Einzelbeispiele. Eine
erfahrungsabhaengige Holdout-Generalisation ist mit dieser Fixture nicht
entscheidbar.

Ausserdem liegen mehrere Druckfenster auf den 24 beobachteten Audiobaendern
innerhalb der Fast-Schwelle `0.2`. Der kleinste gemessene Abstand betraegt
nahezu null. Ein spaeter auditiver Teilscan waere daher nicht frei von
A-Treffern der Druckinhalte.

## Bestandene Teilbedingungen

- beide visuellen Holdout-/Update-Geometrien;
- F/G-Trennung waehrend Training und Prototypfortschreibung;
- familienfremde Holdout-Abweisung;
- q01/q03 eindeutig und q09 ohne visuellen Kandidaten;
- q07/q08 mit positiver Reserve;
- q10 innerhalb beider auditiver Slow-Radien;
- `d_observed(F,G) = 0.02206876019012743`, also
  `0.02 < d <= 0.04`;
- neun Druckrollen untereinander sowie gegen Training in Fast- und
  Slow-Banken getrennt;
- schwache Spur W von F/G getrennt.

Diese Teilbedingungen aendern den terminalen Gesamtstatus nicht.

## Integritaet

- Rezeptorendpunkte: `48`;
- Memoryaufrufe: `0`;
- Feldaufrufe: `0`;
- Kontextaufrufe: `0`;
- Fixture-Suchen: `0`;
- Parameteranpassungen: `0`;
- Gate nach dem Lauf: `False`;
- Quellhash vor/nach: identisch,
  `aaf40a0ee5834120d0ba29cc555cbe3bab2b3ed51ed7d87a30b1bc3274d3f24f`;
- Ergebnisdigest:
  `c29f2c813cc422008eaaa14fb908cee33fdf22317bd71a80ea19a7e64f74bff4`.

Der vollstaendige maschinenlesbare Befund steht in `materialization.json`.

