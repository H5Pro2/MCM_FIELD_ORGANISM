# Lauf 192

## Forschungsfrage

Geprueft wurde, ob die in Lauf 189 und 191 beobachtete spaetere geometrische
M-Wirkung durch drei vorregistrierte, gleich budgetierte lineare
Standardformen reproduziert wird.

Vertrag:

- `docs/K2_F3_E3_BASELINE_AUDIT_UND_VORREGISTRIERUNG.md`

Kandidat und Baselines verwendeten dieselben zwei kontrollierten Geschichten,
dieselbe Probe, dieselben 84 Orte, denselben skalaren Zusatzstate pro Ort,
dieselben Parameter, dieselbe S/H-Nullangleichung und dieselben vier
Geometriearme. Nach jedem Rezeptor-Abschluss wurde die vollstaendige S/H-
Trajektorie passiv erfasst. Es fand keine Parameteranpassung statt.

## Ergebnis

```text
local-leaky:
  maximales Effektresiduum:       0.6637955656046094
  erklaert Effekt:                nein

local-countervariable:
  maximales Effektresiduum:       0.6463201396963132
  erklaert Effekt:                nein

linear-coupled-field:
  maximales Effektresiduum:       0.04922959490217067
  History-S-Relativresiduum:      0.000029966322845308244
  History-H-Relativresiduum:      0.00002369400012210902
  Probe-S-Relativresiduum:        0.00007034140665934525
  Probe-H-Relativresiduum:        0.000058620522482546375
  erklaert Effekt:                ja
```

Alle Beobachtungstakte stimmten ueberein. Alle drei Baselines bewahrten
Gesamtbudget und Nichtnegativitaet. Die sechs Geometrieeffekte und der
same-changed-Kontrast waren in allen Baselines vorhanden.

Die feste Akzeptanzgrenze betrug `0.05`. Die analytische lineare F3-
Feldbaseline blieb mit `0.04922959490217067` knapp darunter.

## Entscheidung

```text
decision: E3_EXPLAINED_BY_NARROW_BASELINE
```

Die unabhaengige lokale Leaky-Spur und die lineare lokale Gegenvariable
reichen nicht aus. Die staerkere, weiterhin enge lineare gekoppelte Feldform
reproduziert jedoch die vollstaendigen vorregistrierten Effekttrajektorien im
festen Korridor. Damit bleibt fuer die bestehende F3-Form kein zulaessiger E3-
Rest als verteilte kausale Nichtseparierbarkeit offen.

## Konsequenz

Die positive E1- und E2-Evidenz bleibt technisch gueltig: F3 ist ein
langsamer, geometrisch verteilter kausaler Geschichtstraeger. Lauf 192 zeigt
aber, dass diese Wirkung im untersuchten Bereich auf feste lineare gekoppelte
Feldmoden zurueckfaellt.

Deshalb werden auf dieser F3-Form nicht als naechstes Verdichtung, E4,
organisches Vergessen oder Memory behauptet beziehungsweise erzwungen. Die
Implementierung bleibt als transparente Feld- und Gegenbaseline erhalten.

## Grenzen

- Der Lauf widerlegt nicht jede denkbare feldbasierte KI-Architektur.
- Er schliesst nur diesen konkreten F3-Korridor als primaeren Weg zu der
  gesuchten nichtseparierbaren Memory-Funktion.
- Nicht untersucht wurden neue, statisch begruendete Freiheitsgrade.
- Es besteht kein Nachweis von Memory, Organisation, Topologie, Feldzeit,
  innerem Kontext, Semantik oder KI.

## Ergebnisartefakt

```text
reports/mcm_f3_e3_baselines_lauf_192.json
```

## Bester naechster Schritt

Vor neuer Implementierung folgt ein statischer Richtungsentscheid: Gesucht
wird der kleinste zulaessige Freiheitsgrad, der nicht bereits algebraisch auf
lokale Leaky-Zustaende oder feste lineare gekoppelte Feldmoden reduziert.
Dabei bleiben F3 und Lauf 192 verpflichtende Gegenbaselines; eine neue Form
darf nicht nur durch staerkere Nichtlinearitaet, mehr Zustand oder eine
lockere Akzeptanzschwelle erzeugt werden.
