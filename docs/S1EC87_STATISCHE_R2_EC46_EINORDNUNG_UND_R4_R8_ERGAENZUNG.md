# S1-EC87: Statische r2-EC46-Einordnung und r4/r8-Ergaenzung

## Forschungsfrage

Welche Teile des vorregistrierten EC46-Entscheidungsvertrags sind durch den
EC86-r2-Lauf belegt und welche Messungen fehlen noch?

## Statischer Befund

EC86 liefert einen gueltigen `r2`-Messpunkt. Alle drei `r2`-
Ordnungsnullkontrollen sind `0` und liegen innerhalb der unveraenderten
EC46-Absoluttoleranz von `1e-12`. Die aktive `r2`-Ordnungsdifferenz liegt mit
`1.557374244509635e-06` fuer `activation` und
`9.359585484425281e-07` fuer `afterimage` in beiden Komponenten ueber
dieser Toleranz.

Das ist noch kein vollstaendiger EC46-Eingang. In EC46 bezeichnet
`active_s/h` den `r8`-Wert. `coarse_s/h` entsteht aus dem Vektorunterschied
`r2-r4`, `fine_s/h` aus `r4-r8`. Auch die drei Nullkontrollen muessen als
Maximum ueber alle drei Verfeinerungsstufen vorliegen. Diese Werte koennen
aus `r2` nicht rekonstruiert werden.

Entscheidung:
`R2_PARTIAL_EC46_INPUT_VALID_R4_R8_COMPLEMENT_REQUIRED`

## Geschlossener Ergaenzungsvertrag

Fuer `r4` und `r8` wird jeweils dieselbe Struktur wie bei EC86 benoetigt:

- dieselben acht Rollen und dieselbe gemeinsame Probe;
- identischer Beobachtungsraum und identische Neuronenordnung;
- ein frisches identisches Feld je Probe;
- sechs getrennte `activation`-/`afterimage`-Kontraste;
- atomare In-Memory-Skalarquittung;
- keine nachtraegliche Aenderung von Toleranz, Signalmarge oder
  Konvergenzregel.

EC87 legt noch kein Schritt- oder Ressourcenbudget fuer `r4/r8` fest und
autorisiert keine Ausfuehrung. Diese Last muss vor einem Lauf aus den
bestehenden konkreten Verfeinerungsplaenen statisch hergeleitet werden.

## Aussagegrenze

Der `r2`-Befund ist technisch messbar und kontrolliert, aber numerisch noch
nicht ueber Verfeinerungen beurteilt. Es gibt keine EC46-Entscheidung und
keinen Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
Selbstregulations- oder KI-Nachweis.

Am besten geht es mit S1-EC88 weiter: die exakten `r4/r8`-Bildungs- und
Probeschrittbudgets, Objektbindungen und Ressourcenanforderungen statisch aus
den bestehenden Plaenen ableiten. Keine Ausfuehrung.
