# S2-BI: AVPC-1 Funktions- und Falsifikationsvertrag

## Funktion

AVPC-1 untersucht genau eine gerichtete technische Funktion:

```text
fruehere eindeutige Audio-Visual-Ueberlappung
-> begrenzte Relation zwischen Prototypidentitaeten
-> spaetere auditive Probe ohne visuelle Eingabe
-> visuelle Prototypidentitaet oder NO_MATCH
```

Es werden keine Audio- oder Videorohdaten, Objektlabels, Woerter oder
Bedeutungen gespeichert oder ausgegeben.

## Getrennte Phasen

Zuerst werden fuer beide Vergleichsgeschichten dieselben zwei auditiven und
zwei visuellen Prototypidentitaeten gebildet und stabilisiert. Danach werden
die vier unabhaengigen Inhaltszustaende eingefroren.

Erst in einer getrennten Relationsphase werden die reduzierten Frames
read-only den vorhandenen Prototypidentitaeten zugeordnet. Die
Prototypbanken duerfen dabei weder aktualisiert noch ersetzt oder
abgeschwaecht werden. Nur der begrenzte Relationszustand darf sich zwischen
den Geschichten unterscheiden.

Nach einer Luecke folgt genau eine auditive Probe. Ein visueller Probe-Frame
ist in dieser Phase verboten.

## Kausale Paarherkunft

Eine Relation ist nur zulaessig, wenn:

- Audio und Video dieselbe Feldtaktkennung tragen;
- ihr tatsaechliches Fenster einen positiven Schnitt besitzt;
- der auditive Snapshot genau einen visuellen Ueberlappungspartner besitzt;
- der visuelle Snapshot genau einen auditiven Ueberlappungspartner besitzt;
- beide Frames read-only genau einer stabilisierten Prototypidentitaet
  zugeordnet wurden.

Mehrfachueberlappung, fehlende Ueberlappung, externe Paar-IDs und
nachtraegliche Reparatur bilden keine Relation.

## Gekreuzte Geschichten

Beide Geschichten besitzen dieselben Inhaltsinventare und Budgets:

```text
H_LEFT:  A_KEY <-> V_LEFT,  B_CONTROL_KEY <-> V_RIGHT
H_RIGHT: A_KEY <-> V_RIGHT, B_CONTROL_KEY <-> V_LEFT
```

Spaeter wird in beiden Geschichten derselbe `A_KEY` auditiv probiert.
AVPC-1 muss links `V_LEFT` und rechts `V_RIGHT` liefern. Eine zweite
Kontrollprobe mit `B_CONTROL_KEY` muss die jeweils andere visuelle Identitaet
liefern.

Weil die Inhaltsbanken waehrend der Relationsphase eingefroren sind, koennen
unterschiedliche PPB-Updates oder Slotreihenfolgen das Ergebnis nicht
erklaeren.

## Gegenbaselines

Getrennte statische oder adaptive Prototypbanken besitzen keine
modalitaetsuebergreifende Relation. Auch die letzte visuelle Lage sagt wegen
der Kontrollpaar-Reihenfolge jeweils die falsche Zielidentitaet voraus.

Replay ist nur eine Kontrolle mit hoeherem Informationsbudget. Die staerkste
faire Baseline ist eine kapazitaetsgleiche heteroassoziative
Naechster-Prototyp-Tabelle. Eine gemeinsame verkettete Prototypbank ist die
einfachere modalitaetsuebergreifende Kontrolle.

Erklaert die staerkste Baseline AVPC-1, bleibt die Funktion eine generische,
MCM-kompatible Engineeringkomponente. Daraus entsteht kein besonderer
Feldmechanismus.

## Falsifikation

AVPC-1 wird gestoppt, wenn die gekreuzten Geschichten nicht mit identischen
eingefrorenen Inhaltszustaenden und gleichen Budgets materialisierbar sind,
wenn die Paarung ein externes Label benoetigt oder wenn die spaetere Probe
visuelle Eingabe beziehungsweise Rohhistorie verwendet.

Unbekannte oder widerspruechlich relationierte auditive Schluessel muessen
`NO_MATCH` liefern. Jede Zustandsaenderung waehrend der Probe macht den
Ablauf ungueltig.

## Naechster Schritt

S2-BJ prueft rein statisch, ob die gekreuzten Fenster, Randzustaende,
Budgets, Paarprovenienz und Gegenbaselines eindeutig materialisierbar sind.
Es werden weiterhin keine Parameter, Fixtures, Funktionen oder Tests
ausgefuehrt.
