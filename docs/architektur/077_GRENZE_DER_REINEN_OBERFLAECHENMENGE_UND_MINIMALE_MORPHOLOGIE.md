# Grenze der reinen Oberflächenmenge und minimale Morphologie

## Fragestellung

Der Zulassungsrahmen könnte jetzt beliebige materialerhaltende Vorschläge
prüfen. Vor einer ersten Gleichung muss jedoch geklärt werden, ob der heutige
Zustand überhaupt eine strukturelle Kontaktbildung darstellen kann.

Aktuell besitzt jede lokale Richtung nur:

```text
surface_material >= 0
```

Dieser Wert sagt, wie viel Eigentümermaterial einer Richtung zugeordnet ist.
Er sagt nicht:

- wo sich das Material innerhalb dieser Richtung befindet;
- wie weit es räumlich reicht;
- ob es eine gegenüberliegende Oberfläche berührt;
- ob zwei Materialformen getrennt oder verbunden sind.

## Klasse A - Direkte Flussintegration

Eine naheliegende Fortschreibung wäre:

```text
Delta s_i,r proportional zu J_i,r
```

oder zu Betrag beziehungsweise Quadrat des gerichteten Feldflusses.

Diese Klasse speichert eine zeitliche Summe schneller Feldwirkung. Mit
Rückführung oder festem Rückzug wird sie zu:

- Flussintegrator;
- Leaky-Spur;
- sättigender Spur;
- vorzeichenabhängiger Richtungsdisposition.

Sie löst die bekannten Grenzen nicht.

## Klasse B - Normalisierte lokale Konkurrenz

Die endliche Materialbilanz könnte Material proportional zu den momentanen
Richtungsursachen verteilen:

```text
s_i,r = M_i * normierte_Ursache_i,r
```

Eine weiche Normierung vermeidet einen expliziten Gewinner, legt aber dennoch
eine feste Auswahlfunktion fest. Der Zustand ist dann entweder:

- momentane Projektion ohne Memory;
- geglättete Projektion mit Leaky-Memory;
- Softmax- oder Rangmechanik mit programmierter Konkurrenz.

Auch diese Klasse erzeugt keine neue strukturelle Funktion.

## Klasse C - Multiplikative oder replikative Umverteilung

Eine zustandsabhängige Konkurrenz kann vorhandene Oberflächenmengen durch
lokale Ursachen vermehren oder verdrängen, während die Summe erhalten bleibt.

Diese Klasse ist kontinuierlich und symmetrisch formulierbar. Dennoch gilt:

- Oberflächenmengen wirken wie adaptive Richtungsgewichte;
- exakt null gewordene Anteile können absorbierend werden;
- erneutes Wachstum benötigt eine zusätzliche Einspeisung aus dem
  ungebundenen Anteil;
- Stabilität und Lösung liegen in der gewählten Wachstumsfunktion.

Ohne zusätzliche räumliche Bedeutung ist dies eine budgetierte
Gewichtsdynamik.

## Klasse D - Gegenseitiger Mengenleser

Zwei gegenüberliegende Oberflächen könnten über eine Funktion wie

```text
K_ij = s_i,r * s_j,-r
```

oder

```text
K_ij = min(s_i,r, s_j,-r)
```

gekoppelt werden.

Damit würde die Beziehung direkt aus zwei skalaren Mengen als Stärke
berechnet. Der Partner wäre zwar nicht im Zustand gespeichert, die feste
Geometrie rekonstruiert aber dieselbe lokale Kante.

Funktional entsteht erneut ein adaptives Kantengewicht.

## Klasse E - Schwellenkontakt

Man könnte Berührung definieren als:

```text
s_i,r > Schwelle
und
s_j,-r > Schwelle
```

Dann entstehen exakte Verbindung und Lösung. Ihre Grenze ist jedoch vollständig
im programmierten Schwellwert enthalten. Das wäre ein Kontaktautomat, keine
entstandene räumliche Berührung.

## Enger Befund

Die heutige Oberflächenmenge ist ein sinnvoller Bilanzzustand, aber noch kein
vollständiger Strukturzustand.

```text
Materialmenge pro Richtung
ohne räumliche Lage oder Ausdehnung
-> kein geometrischer Kontakt unterscheidbar
-> funktionale Nutzung fällt auf Gewicht oder Schwelle zurück
```

Das widerlegt nicht das strukturelle Kontaktsubstrat. Es zeigt, dass seine
erste Anatomie nur Eigentümerschaft und Materialbilanz trägt.

## Warum räumliche Morphologie eine andere Klasse wäre

Wenn Eigentümermaterial zusätzlich eine lokale räumliche Lage oder
Ausdehnung besitzt, können Zustände unterschieden werden wie:

```text
Material vorhanden, aber zurückgezogen
Material in Richtung einer Oberfläche verlagert
Material erreicht die lokale Grenzfläche
gegenüberliegende Formen berühren sich
Formen trennen sich wieder
```

Dann kann funktionale Lösung durch reale geometrische Trennung eintreten,
obwohl das Material vollständig erhalten bleibt.

Dies ist grundsätzlich etwas anderes als:

```text
Gewicht wird kleiner
oder
Leser unterschreitet Schwelle
```

## Noch keine Darstellung gewählt

Der Befund gibt nicht automatisch frei:

- eine Ausdehnungsvariable;
- Materialpartikel;
- radiale Rasterzellen;
- kontinuierliche Dichte;
- Wachstumsfronten;
- Kollisionsregeln;
- Feder-, Zug- oder Druckkräfte.

Jede dieser Darstellungen bringt eigene programmierte Physik mit. Sie muss
separat begründet und gegen Gewichtsäquivalenz geprüft werden.

## Mindestanforderung an eine Morphologie

Eine spätere räumliche Darstellung müsste mindestens:

1. Material weiterhin einem Neuron zuordnen;
2. dieselbe endliche Eigentümermenge erhalten;
3. Lage oder Ausdehnung relativ zum Eigentümer darstellen;
4. keine Partneridentität speichern;
5. Berührung ausschließlich aus lokaler Geometrie ableiten;
6. Trennung ohne Reset oder Löschbefehl ermöglichen;
7. frei gewordenes Material erneut räumlich verfügbar halten;
8. unter Spiegelung und Achstausch äquivariant bleiben;
9. ohne Feldursache im neutral zurückgezogenen Zustand bleiben;
10. noch keine Feldwirkung besitzen.

## Verhältnis zur bestehenden Umsetzung

Die bisherigen Bausteine bleiben gültig:

- `structural_contact_substrate.py` trägt Eigentümerschaft und Bilanz;
- `structural_contact_drive.py` richtet vorhandene Feldursachen lokal aus;
- `contact_material_admissibility.py` prüft Erhaltung und Symmetrie.

Sie werden nicht zur Memory-Runtime erklärt. Eine mögliche Morphologie würde
diese Grenzen erweitern, nicht umgehen.

## Status

```text
reine Oberflächenmenge als Bilanz brauchbar:          ja
reine Oberflächenmenge als Kontaktstruktur ausreichend: nein
Mengenleser oberhalb adaptiver Gewichte:               nein
Schwellenkontakt zulässig:                              nein
räumliche Morphologie als getrennte Klasse begründet:   ja
konkrete Morphologiedarstellung gewählt:                nein
Materialdynamik freigegeben:                            nein
Runtime-Rückwirkung freigegeben:                        nein
```

## Nächster Schritt

Als Nächstes wird ausschließlich der minimale räumliche Zustandsvertrag
formuliert.

Er muss beantworten:

> Welche kleinste partnerlose räumliche Materialbeschreibung kann Rückzug,
> Annäherung und geometrische Berührung unterscheiden, ohne bereits eine
> Wachstumsregel oder Kontaktwirkung festzulegen?

Erst danach ist entscheidbar, ob eine strukturelle Materialdynamik technisch
mehr sein kann als ein Richtungsgewicht unter anderem Namen.

Dieser
[minimale räumliche Zustandsvertrag](078_MINIMALER_RAEUMLICHER_ZUSTANDSVERTRAG_DES_KONTAKTMATERIALS.md)
wählt nun ein partnerloses radiales Materialprofil je lokaler Richtung.
Räumliche Auflösung, Bewegung, Berührungseffekt und Feldrückwirkung bleiben
weiterhin offen.
