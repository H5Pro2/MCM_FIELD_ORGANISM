# S1-EC97: STOPP - EC46-Differenzvektoren nicht behalten

## Statischer Befund

Die r2-, r4- und r8-Laufergebnisse enthalten die L-infinity-Betraege der
sechs vorregistrierten Kontraste. Alle drei Nullkontrollen sind ueber alle
Verfeinerungen exakt null und die aktiven Skalarbetraege sind vorhanden.

EC46 verlangt fuer die Konvergenzentscheidung jedoch mehr als diese
Betraege. Der Vertrag bildet zuerst fuer jede Verfeinerung den vollstaendigen
aktiven AB-minus-BA-Differenzvektor und berechnet danach:

- `coarse = ||Differenzvektor(r2) - Differenzvektor(r4)||_inf`;
- `fine = ||Differenzvektor(r4) - Differenzvektor(r8)||_inf`.

Erforderlich sind daher sechs Vektoren: Aktivierung und Nachhall fuer r2,
r4 und r8. EC86 und EC96 haben nach der atomaren Reduktion nur deren
L-infinity-Betraege zurueckgegeben. Die nicht persistenten Prozesse sind
beendet und die EC96-Autorisierung ist verbraucht.

## Warum keine Rekonstruktion zulaessig ist

Aus `||v||_inf` und `||w||_inf` folgt der Wert von `||v-w||_inf` nicht.
Vektoren mit denselben Einzelbetraegen koennen je nach Richtung und
Komponentenlage unterschiedliche Abstaende besitzen. Die Differenz der
Skalarbetraege ist lediglich eine untere Schranke und kein Ersatz fuer den
von EC46 vorregistrierten Vektorabstand.

Entscheidung: `STOP_EC46_RAW_ORDER_VECTORS_NOT_RETAINED`.

Dies ist keine Widerlegung der gemessenen zustandsabhaengigen Feldantwort
und keine wissenschaftliche Sackgasse des E1-Kandidaten. Es ist eine harte
Datenvertragsluecke der Konvergenzauswertung. Eine EC46-Entscheidung waere
mit dem aktuellen Bestand freie Interpretation und bleibt verboten.

Es besteht weiterhin kein Memory-, Feldzeit-, Organisations-, Topologie-,
Semantik-, Selbstregulations- oder KI-Nachweis.

Am besten geht es mit S1-EC98 weiter: einen korrigierten atomaren
Vektorquittungsvertrag entwerfen, der ausschliesslich die sechs aktiven
AB-minus-BA-Differenzvektoren und die bereits gebundenen Kontrollskalare
zurueckgibt. Noch keine Ausfuehrung. Erst nach synthetischer Abnahme und
neuer ausdruecklicher Besitzerfreigabe duerfte eine minimale erneute
Messung diskutiert werden.
