# S2-BB: Quellgebundener Baseline-Materialisierungsvertrag

## Zweck

S2-BB bindet den spaeteren Vergleich des privaten PPB-1-Bildungs-und-
Abrufpfads mit genau einer einfachen statischen Prototypbank. Der Vertrag
enthaelt noch keinen Code und keine Ausfuehrung.

## Gemeinsame Quelle

Kandidat und Baseline muessen dasselbe unveraenderliche aktive
Rezeptor-Batch, dasselbe Profil und dieselben auditiven und visuellen
Bildungsvektoren in derselben Reihenfolge erhalten. Auch die spaetere Probe,
die Distanzfunktion und die Entscheidungsschwelle sind identisch gebunden.

Die Baseline darf keine Prototypwerte, Slot-IDs, Supportzaehler oder
Stabilitaetsereignisse aus dem PPB-1-Nachzustand lesen.

## Statische Prototypbaseline

Pro Modalitaet existiert genau ein privater Prototypvektor:

1. Der erste reduzierte Bildungsvektor initialisiert den Prototyp.
2. Weitere Bildungsvektoren werden in Quellreihenfolge mit derselben im
   Profil gebundenen Aktualisierungsrate verarbeitet.
3. Liegt ein weiterer Vektor ausserhalb der gemeinsamen Matchschwelle, ist
   der Ein-Prototyp-Vergleich methodisch ungueltig.
4. Nach der Bildung wird der Prototyp eingefroren.
5. Die spaetere Probe berechnet nur die vorhandene normalisierte
   L1-Distanz. Der Baselinezustand bleibt unveraendert.

Die Baseline besitzt keine Slots, Supportfortschreibung, Stabilitaetsrolle,
Ablaufregel, Verdraengung oder Replayhistorie.

## Atomare Auswertung

Alle Kandidaten- und Baselinebefunde werden zuerst lokal vollstaendig
gebildet und ihre Quellen sowie Vor- und Nachdigests erneut geprueft. Erst
danach darf genau ein gemeinsamer Receipt entstehen. Jeder Teilfehler,
Quellunterschied oder jede Zustandsaenderung verwirft den ganzen Vergleich.

Zulaessige spaetere Klassifikationen sind:

- `BASELINE_EXPLAINS_CURRENT_FIXTURE`;
- `UNEXPECTED_DIFFERENCE_REQUIRES_STATIC_AUDIT_NO_ADVANTAGE_DECISION`;
- `METHOD_INVALID_NO_PAIRED_RESULT`.

Eine Vorteilsklassifikation ist nicht vorgesehen. Bei identischer
Operations- und Eingabereihenfolge waere ein Unterschied zuerst als
technischer Widerspruch zu pruefen.

## Aktuelle Gegenprognose

Die aktuelle Fixture verwendet pro Modalitaet drei identische
Bildungsvektoren. Deshalb werden fuer PPB-1 und Baseline derselbe Prototyp,
dieselben Distanzen und dieselben positiven beziehungsweise negativen
Entscheidungen erwartet. Der Lauf kann spaeter Baseline-Erklaerbarkeit
bestaetigen, aber keinen PPB-1-Vorteil zeigen.

## Grenze und naechster Schritt

S2-BB aendert weder API, Snapshot, Feldkern noch Produktionspfad. Es entsteht
kein Feldwirkungs- oder MCM-Memory-Befund.

Naechster Schritt ist S2-BC: ein statischer Preflight auf eindeutige
Materialisierbarkeit, Nichtzirkularitaet und Ausschluss von Informationsfluss
aus dem Kandidatenzustand in die Baseline. Implementierung und Ausfuehrung
bleiben gesperrt.
