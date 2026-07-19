# Methodischer Abschluss von Lauf 095

## Zweck

Dieser Abschluss gleicht
[Befund 014](../forschung/014_PASSIVER_VERDECKUNGSWELT_INTERVENTIONSBEFUND.md)
vollständig mit der
[Vorregistrierung 095](095_VORREGISTRIERUNG_PASSIVE_VERDECKUNGSWELT_INTERVENTIONSFAMILIE.md)
ab.

Er ergänzt keine Mechanik und wertet Lauf 095 nicht als Memory-Untersuchung.

## Abgleich

| Vorregistrierte Bedingung | Umsetzung | Ergebnis |
|---|---|---|
| V0: sichtbare Richtungserhaltung | `1 -> 2` | erfüllt |
| V1: sichtbare Richtungsumkehr | `1 -> 0` | erfüllt |
| H0: verdeckte Richtungserhaltung | `2 -> 3 -> 4 -> 5 -> 6 -> 7` | erfüllt |
| H1: verdeckte Richtungsumkehr | `2 -> 3 -> 4 -> 3 -> 2 -> 1` | erfüllt |
| dieselbe Weltregel sichtbar und verdeckt | gemeinsame signierte Richtungsfunktion | erfüllt |
| gleiche Vorgeschichte H0/H1 bis `t2` | `2 -> 3 -> 4` | erfüllt |
| kontaktfreie verdeckte Projektion | Positionen `3`, `4`, `5` ergeben Nullkontakt | erfüllt |
| gleiche V-Budgets | je zwei Rahmen | erfüllt |
| gleiche H-Budgets | je sechs Rahmen, drei Kontakte, drei Nullrahmen | erfüllt |
| feste Holdouts | H0: `6, 7`; H1: `2, 1` | erfüllt |
| spiegelbildliche Holdouts | `6 <-> 2`, `7 <-> 1` | erfüllt |
| P0 nur observerseitig | Ereignis-ID erst nach abgeschlossenem Zweig | erfüllt |
| keine Ereignis-ID beim Wiederkontakt | Runtime-Rollen enthalten keine Ereignis-ID | erfüllt |
| keine Auswahl anhand späterer Feldantwort | Weltfolgen vor Ausführung fest | erfüllt |
| Reihenfolgeneutralität | umgekehrte Zweigreihenfolge ergibt denselben Befund | erfüllt |
| Wiederholbarkeit | kanonischer Ergebnisdigest bleibt identisch | erfüllt |
| Observerneutralität | unveränderliche Zweigbeobachtungen | erfüllt |
| keine künstliche Rauschquelle | keine Zufalls- oder Rauschfunktion vorhanden | erfüllt |
| keine künstliche Varianz | konstante Geometrie, Lage und Reizstärke | erfüllt |
| keine Ruhepunktdynamik | ausschließlich `receptor_projection_baseline` | erfüllt |
| keine neue Speichergröße | keine Runtime-Rolle ergänzt | erfüllt |
| keine Rückschreibung | Observer bleibt passiv | erfüllt |

## Erklärungsgrenze

Jeder beobachtete MCM-Ausgang ist vollständig erklärt durch:

```text
aktuelle Weltposition
-> aktuelle sichtbare Projektion
-> aktueller Rezeptorkontakt
-> receptor_projection_baseline
```

Die verdeckte Weltbewegung ist eine fortgesetzte Außenweltursache. Der
Wiederkontakt enthält keine intern gespeicherte Konsequenz.

## Vollständige Gegenwartsangleichung

Für die nächste Nullkontrolle ist eine technische Präzisierung verbindlich.
Die bekannte MCM-Perzeption enthält neben dem aktuellen Rezeptorkontakt lokale
Feldproben aus dem unmittelbar vorherigen Takt.

Deshalb gilt:

```text
ein identischer Proberahmen
-> gleiche activation und gleicher afterimage
-> aber noch keine garantierte Gleichheit des vollständigen Feld-Snapshots
```

Erst ein zweiter identischer Proberahmen kann auch die bekannte lokale
Ein-Schritt-Probe angleichen:

```text
Probe A: Angleichungsrahmen
Probe B: identische Holdoutprobe nach vollständiger bekannter Angleichung
```

Diese Ein-Schritt-Zeitlage ist Bestandteil der vorhandenen Feldwahrnehmung.
Sie ist keine neue Speichermechanik und darf nicht als Memory bezeichnet
werden.

## Abschluss

Lauf 095 erfüllt die Vorregistrierung. Sein Befund bleibt:

> Die vorhandene Welt-, Rezeptor- und MCM-Kette transportiert aktuelle
> sichtbare Weltursachen deterministisch. Sie zeigt in diesem Lauf keine
> Speicherwirkung.

## Wie es am besten weitergeht

Als Nächstes wird die zweistufige identische spätere Weltprobe als reine
Null- und Wiederholbarkeitskontrolle vorregistriert. Entscheidend ist die
getrennte Ausweisung von Ausgang nach Probe A und vollständigem Snapshot nach
Probe B. Ein Gleichlauf bestätigt nur die bestehende Runtime; ein Rest würde
zuerst auf unvollständige Zustandsangleichung oder Metadatenleck geprüft.
