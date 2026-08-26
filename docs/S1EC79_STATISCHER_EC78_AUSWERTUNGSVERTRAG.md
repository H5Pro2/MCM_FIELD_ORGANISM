# S1-EC79: Statischer EC78-Auswertungsvertrag

## Forschungsfrage

Reicht der nach EC78 erhaltene Befund fuer eine quantitative Entscheidung
nach dem vorregistrierten EC46-Vertrag aus?

## Quellen

- der exakt gehashte EC78-Laufbericht;
- EC45 als Identifizierbarkeitsvertrag fuer acht Rollen und sechs Kontraste;
- EC46 als vorregistrierter numerischer Akzeptanzvertrag;
- die EC63-Probequittungen mit geordneten `activation`- und
  `afterimage`-Vektoren.

## Statischer Befund

EC78 belegt die technische Vollendung von vier Formationen, acht frischen
Feldern, acht Proben und 3.208 Feldschritten. Die Rollenstruktur stellt auf
`r2` alle sechs vorgesehenen Kontraste bereit.

Die nicht persistente Ausfuehrung hat jedoch weder die acht Probevektoren
noch daraus gebildete EC46-Skalare erhalten. Der Ergebnis-Digest erlaubt
keine Rekonstruktion dieser Werte. Zudem verlangt EC46 ein festes
Verfeinerungsprofil aus `r2`, `r4` und `r8`; EC78 lief nur mit `r2`.

Entscheidung:
`EC78_TECHNICALLY_COMPLETE_QUANTITATIVE_EVALUATION_UNAVAILABLE`

## Grenzen und Gegenbaselines

Strukturell vorgesehen, quantitativ aber nicht erhalten, sind:

- P0-Reset AB gegen BA als Sanitaetskontrolle;
- E1 aktiv AB gegen BA als Ordnungsdifferenz;
- Probe-Rueckwirkungsablation AB gegen BA;
- Bildungsablation AB gegen BA;
- aktiv gegen Probe-Rueckwirkungsablation fuer AB und BA;
- `activation` und `afterimage` jeweils getrennt;
- `r2/r4/r8` als notwendige numerische Konvergenzbaseline.

Aus dem EC78-Bericht darf deshalb weder ein Zahlenwert ergaenzt noch eine
Wirkung abgeleitet werden. Es gibt keinen Memory-, Feldzeit-, Organisations-,
Topologie-, Semantik-, Selbstregulations- oder KI-Nachweis.

## Naechster zulaessiger Schritt

Vor einer neuen Ausfuehrung muss ein in-memory Auswerter entworfen werden,
der die acht Probequittungen unmittelbar im selben Prozess in die
vorregistrierten Kontraste umwandelt. Eine spaetere Ergebnisquittung darf nur
die notwendigen Skalarwerte, Rollen- und Quelldigests tragen; Rohfelder oder
ein rekonstruierbares Memory werden nicht persistiert. Der Auswerter muss
zuerst ausschliesslich synthetisch abgenommen werden.

Am besten geht es mit S1-EC80 weiter: einen nicht ausfuehrenden, typisierten
Kontrast- und Skalarvertrag fuer genau eine `r2`-Ergebnisquittung definieren.
Dieser Vertrag darf noch keine EC46-Gesamtentscheidung treffen, weil `r4`
und `r8` fehlen.
