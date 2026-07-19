# Passiver Zulassungsrahmen für Materialfortschreibungen

## Zweck

Der Materialbilanz- und Symmetrievertrag ist jetzt als technische
Prüfschicht umgesetzt.

Der Rahmen erzeugt keine Materialdynamik. Er nimmt ausschließlich einen
vollständig vorgeschlagenen Folgezustand entgegen und prüft, ob dieser die
festgelegten physischen Grenzen verletzt.

```text
Materialzustand(t)
+ vorhandene lokale Feldursachen
+ externer passiver Kandidatenvorschlag
-> Zulassungsprüfung
-> Bericht
```

Der vorgeschlagene Zustand wird nicht in das MCM-Feld übernommen.

## Geprüfte Grenzen

`audit_contact_material_proposal` prüft:

- korrekte Herkunftsdigests;
- genau einen atomaren Materialtakt;
- unveränderte Layer- und Geometrieidentität;
- dieselben lokalen Eigentümer;
- unveränderte Eigentümerpositionen;
- unveränderte Gesamtmenge jedes Neurons;
- dieselben lokalen Oberflächenrichtungen;
- vollständige lokale Materialbilanz;
- Nichtnegativität;
- Neutralität bei neutralem Material und vollständig fehlender Feldursache.

Eine bestandene Prüfung bedeutet nur:

> Dieser Vorschlag verletzt die gegenwärtigen Mindestgrenzen nicht.

Sie bedeutet nicht:

- dass seine Dynamik organisch ist;
- dass er Memory trägt;
- dass er an die Runtime angeschlossen werden darf.

## Symmetrieprüfung

`SignedAxisTransform` beschreibt ausschließlich Spiegelung, Achsentausch und
deren Kombination.

`audit_contact_material_symmetry` vergleicht:

```text
transformierter Ausgangszustand
+ transformierte lokale Feldursachen
-> muss transformierten Materialvorschlag ergeben
```

Dabei werden Positionen statt Neuronenbezeichnungen verglichen. Eine feste
Richtungsbevorzugung fällt dadurch durch die Prüfung.

Die Prüfung beweist keine vollständige Symmetrie einer Regel. Sie widerlegt
aber bereits Kandidaten, deren Vorschlag in einer kontrollierten
Transformation nicht mitwandert.

## Nullgrenze

Im neutralen Materialzustand ohne Aktivierung, lokalen Fluss oder
Rezeptorkontakt darf kein Oberflächenmaterial entstehen.

Ein Vorschlag, der in diesem Zustand Struktur erzeugt, wird abgelehnt.

Diese Kontrolle betrifft nur den neutralen Anfang. Sie legt keine spätere
Relaxations- oder Offline-Dynamik fest.

## Technischer Nachweis

Die fokussierten Kontrollen zeigen:

- lokal erhaltener Materialvorschlag wird angenommen;
- veränderte Eigentümergesamtmenge wird abgelehnt;
- spontane Struktur aus neutraler Nullursache wird abgelehnt;
- korrekt gespiegelter Vorschlag wird als äquivalent erkannt;
- feste Richtungsbevorzugung scheitert an der Spiegelprüfung;
- kein angenommener Vorschlag erhält Runtime-Freigabe.

## Architekturgrenze

Der Rahmen besitzt:

- keine Kandidatenregel;
- keine Standardfortschreibung;
- keine Wachstums- oder Rückzugsrate;
- keine Schwelle;
- keinen Gewinner;
- keinen Beziehungszustand;
- keine Feldwirkung;
- keine Runtime-Anwendung.

Er ist ein Laborrahmen für spätere passive Kandidaten, kein Teil des lebenden
Organismus.

## Status

```text
Bilanzprüfung umgesetzt:                    ja
Eigentümererhaltung geprüft:                ja
Nullinvarianz geprüft:                      ja
Spiegel- und Achstransformation prüfbar:    ja
konkrete Materialdynamik vorhanden:         nein
Materialzustand fortgeschrieben:            nein
Runtime-Rückwirkung freigegeben:            nein
organisches Memory gezeigt:                 nein
```

## Nächster Schritt

Vor einem ersten Materialkandidaten muss die kleinste zulässige
Umverteilungsfrage präzisiert werden:

> Kann eine einheitliche lokale Wechselwirkung Material kontinuierlich
> zwischen ungebundenem Anteil und Oberflächen verschieben, ohne
> Flussakkumulator, Schwelle, Richtungsgewinner oder feste Zerfallsspur zu
> werden?

Zuerst werden Kandidatenklassen gegeneinander abgegrenzt. Eine Gleichung wird
erst implementiert, wenn mindestens eine Klasse nicht bereits auf die
bekannten Leaky-, Integrator-, Schwellen- oder Kantengewichtsbaselines
zurückfällt.
