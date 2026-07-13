# MCM Field Organism

## Ziel

Dieses Projekt untersucht ein digitales, MCM-basiertes Nervensystem in einem
geschlossenen Weltkreislauf.

Die grundlegende Arbeitshypothese lautet:

```text
dieselben lokalen MCM-Träger
+ schnelle innere Feldzustände
+ mögliche langsamere lokale Organisationszustände
+ Rezeptoren und Effektoren
= ein entwicklungsfähiger Nervensystemkandidat
```

Der Projektname bezeichnet die Forschungsrichtung. Ein Organismus,
Selbsterhaltung, Lernen oder Feldintelligenz sind noch nicht gezeigt.

## Grundarchitektur

```text
WELT
↕
REZEPTOREN UND EFFEKTOREN
↕
GEMEINSAME LOKALE MCM-TRÄGER
├─ schnelle Innenzustände
├─ mögliche langsamere Kopplungszustände
└─ lokale begrenzte Ressourcen

OBSERVER
└─ liest passiv und schreibt nichts zurück
```

Das schnelle MCM-Innenfeld soll aktuelle Aktivierung, Überlagerung, Nachhall
und kurzfristige Feldgeschichte tragen.

Eine langsamere Organisationsgeschichte darf später nur an oder zwischen
denselben Trägern entstehen. Ein separates Muster-, Syntax- oder Gedächtnisnetz
ist nicht vorgesehen.

## Keine fertigen kognitiven Module

Die folgenden Begriffe sind zunächst ausschließlich Forschungs- und
Beobachtungsbegriffe:

- Muster
- Syntax
- Verdichtung
- Kontext
- Reflexion
- Sleep
- Reorganisation

Sie werden nicht als Runtime-Module eingebaut. Erst ein beobachteter und
kausal geprüfter Feldvorgang darf später mit einem dieser Begriffe beschrieben
werden.

## Aktueller Stand

Das Projekt befindet sich in der konzeptionellen Gründungsphase.

Noch nicht vorhanden oder freigegeben sind:

- Runtime-Code
- konkrete MCM-Gleichungen
- Kopplungsvariable
- Lern- oder Bildungsregel
- Ressourcenfluss
- automatische Topologieentwicklung
- Reflexion oder Sleep-Mechanik
- autonome Handlung

## Dokumentation

- [Gründungsvertrag](docs/GRUENDUNGSVERTRAG.md)
- [Offene Forschungsfragen](docs/FORSCHUNGSFRAGEN.md)
- [Dokumentationsübersicht](docs/README.md)

## Nächster methodischer Schritt

Vor Runtime-Code muss die erste passive Systemgrenze festgelegt werden:

```text
reale oder simulierte Weltwirkung
-> lokaler Rezeptorkontakt
-> schneller MCM-Innenzustand
-> passive Beobachtung
```

Effektoren werden als notwendiger Teil der Gesamtarchitektur berücksichtigt.
Eine langsame Organisationsgeschichte bleibt gesperrt, bis ein stabiler,
kausaler Weltkreis ohne Lernen geprüft wurde.
