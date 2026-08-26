# S2-BA: Technischer Wiedererkennungs-Baselineaudit

## Auftrag

S2-BA prueft statisch, welche bestehende Baseline den privaten technischen
Pfad aus Zustandsbildung, Stabilisierung und spaeterer read-only Probe am
staerksten und fairsten kontrolliert. Es wurde nichts implementiert oder
ausgefuehrt.

## Auswahl

Die `SIMPLE_STATIC_PROTOTYPE_BANK` ist die primaere Baseline. Sie erhaelt
dieselben verdichteten Bildungseingaben und nutzt dieselbe normalisierte
L1-Distanz mit derselben modalitaetsspezifischen Schwelle. Anders als PPB-1
besitzt sie keine Slot-Lebenszyklen, Supportfortschreibung oder
Stabilitaetsidentitaet.

Die Distanz zum letzten Bildungsvektor bleibt eine minimale
Kontrollbaseline. Weil alle drei aktuellen Bildungsvektoren identisch sind,
sind letzter Vektor und daraus gebildeter statischer Prototyp in der
vorliegenden Fixture gleich. Die statische Prototypbank ist trotzdem die
staerkere allgemeine Kontrolle.

## Befund

Die aktuelle Fixture enthaelt keine eigenstaendige Gegenprognose:

- PPB-1 und statische Prototypbank erwarten fuer die identische spaetere
  Probe eine positive Wiedererkennung.
- Beide erwarten fuer die weit ausserhalb der Schwelle liegende Probe eine
  negative Wiedererkennung.
- Unterschiedliche Digests, Slotrollen oder Receipts waeren kein
  Funktionsvorteil.

Der private Bildungs-und-Abruf-Pfad bleibt ein belastbarer technischer
Grundpfad. Die aktuelle Wiedererkennung ist jedoch fuer diese Fixture durch
die einfache statische Prototypbank erklaerbar.

## Offene Materialisierung

Der vorhandene S1-YA-Code ist an die aeltere S1-XZ-Fixture gebunden und kann
nicht unveraendert an den aktiven Rezeptorumschlag angeschlossen werden. Vor
einem Vergleich fehlen deshalb:

1. eine private quellgebundene Baseline-Huelle fuer denselben aktiven Batch;
2. ein atomarer gemeinsamer Receipt- und Comparatorvertrag;
3. eine ausdrueckliche Behandlung der fehlenden Gegenprognose der aktuellen
   Fixture.

S1-YE bleibt verbindlich: Eine zweite adaptive Online-Prototypbank wird nicht
erneut geoeffnet, weil sie PPB-1 in derselben Mechanismusfamilie dupliziert.

## Grenze und naechster Schritt

S2-BA ist weder Vergleichsausfuehrung noch Nachweis eines PPB-1-Vorteils,
einer Feldwirkung oder einer MCM-spezifischen Memory-Mechanik.

Naechster Schritt ist S2-BB: ein rein statischer Materialisierungsvertrag fuer
die quellgebundene aktive statische Prototypbaseline, den gepaarten Receipt
und die Comparatorreihenfolge. Implementierung und Ausfuehrung bleiben bis
dahin gesperrt.
