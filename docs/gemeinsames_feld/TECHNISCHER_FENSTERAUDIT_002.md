# Technischer Fensteraudit 002

## Status

Technische Voruntersuchung vor `GF_001`.

Dieser Audit erzeugt keinen gemeinsamen MCM-Feldzustand. Er prüft nur, welche
vollständig reduzierten nativen Rezeptorzustände in gemeinsame Zeitfenster
fallen, die bereits vor dem ersten Sensor-Read feststehen.

## Vertrag

Der Zeitplan legt auf `organism.monotonic_ns` vorab fest:

- den Beginn der Fensterfolge,
- die unveränderte Breite jedes Fensters,
- die Anzahl lückenlos aufeinanderfolgender Fenster.

Ein Rezeptorzustand wird genau dann einem Fenster zugerechnet, wenn sein
gemessenes Read-Intervall vollständig darin liegt. Ein Read über eine Grenze
bleibt als Grenzübertritt sichtbar. Zustände außerhalb der Folge bleiben
außerhalb.

Der Audit verwendet keine Auswahl, Mittelung, Interpolation, Wiederholung,
Sample-and-Hold-Regel oder Rohdatenhaltung.

## Synthetische Gegenprüfungen

Sieben Kontrollen belegen:

1. genau ein Zustand je Modalität und Fenster wird als solcher ausgewiesen,
2. mehrere Zustände werden gezählt und nicht ausgewählt,
3. fehlende Zustände bleiben als Anzahl null sichtbar,
4. grenzüberschreitende Reads werden keinem Fenster zugerechnet,
5. die Reihenfolge der Modalitäten verändert das Ergebnis nicht,
6. verschiedene Organismusuhren werden abgewiesen,
7. das öffentliche Ergebnis enthält keine Reduktions- oder Auswahlrolle.

## Realer Lauf

Drei gemeinsame Fenster mit je einer Sekunde wurden vor dem ersten Read
deklariert. Kameraeingang `0` und Audioeingang `1` waren die bereits technisch
bestätigten Geräte.

| Fenster | Auditive Zustände | Visuelle Zustände |
|---:|---:|---:|
| 0 | 108 | 5 |
| 1 | 101 | 4 |
| 2 | 98 | 4 |

Zusätzlich wurden sechs grenzüberschreitende Zustände und kein Zustand
vollständig außerhalb der Fensterfolge gemessen. Insgesamt entstanden 310
auditive und 16 visuelle reduzierte Zustände. Kein Fenster enthielt genau
einen Zustand beider Modalitäten.

Rohbilder und Audiosamples wurden nicht im Auditergebnis gehalten.

## Befund

Ein vorab gemeinsamer technischer Zeitrahmen ist real ausführbar. Er löst die
unterschiedlichen nativen Rezeptorraten jedoch nicht:

```text
gemeinsames vorab festgelegtes Fenster
!= genau ein nativer Zustand je Dock
!= gemeinsamer MCM-Feldzustand
```

Eine nachträgliche Auswahl eines Audio- oder Videozustands wäre eine technisch
eingebaute Fusionsregel. Das wurde nicht vorgenommen.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Der nächste Schritt liegt innerhalb der Rezeptorgrenze: Jeder Rezeptor müsste
ein gemeinsames Organismusfenster selbst vollständig aufnehmen und daraus
genau eine abgeschlossene technische Lage bereitstellen. Die Reduktion muss
modalitätseigen, vorregistriert und gegen Auslassen, Mittelung und versteckte
Sample-and-Hold-Wirkung kontrolliert werden. Der Rezeptorenverteiler darf diese
Arbeit nicht nachträglich übernehmen.

Noch nicht freigegeben sind:

- ein gemeinsamer fortlaufender MCM-Feldtakt,
- Feldkopplung,
- Topologie oder Memory,
- Semantik,
- Selbstregulation.
