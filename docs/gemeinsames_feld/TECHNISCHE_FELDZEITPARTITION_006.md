# Technische Feldzeitpartition 006

## Status

Technische Voruntersuchung vor `GF_001`.

Die Partition erzeugt keinen MCM-Feldzustand. Sie zerlegt ausschließlich einen
begrenzten realen Beobachtungshorizont an den gemessenen Abschlusszeiten
nativer Rezeptorzustände in lückenlose `MCMFieldStepTime`-Spannen.

## Vertrag

Für einen vorab bekannten Horizont gilt:

- Start und Ende bleiben unverändert,
- jede Abschlusszeit innerhalb des Horizonts wird eine Grenze,
- Ereignisse gleicher Abschlusszeit bleiben gemeinsam und ungeordnet,
- jedes Ereignis bleibt an seiner gemessenen Grenze,
- ein ereignisfreier Rest bleibt als leere Zeitspanne sichtbar,
- vor oder nach dem Horizont abgeschlossene Zustände bleiben explizit außen.

Nicht angewendet werden Halten, Auswahl, Interpolation, Rekonstruktion,
Ratenangleichung oder Feldfortschaltung.

## Synthetische Kontrollen

Sechs Kontrollen zeigen:

1. die Zeitspannen decken den Horizont lückenlos und überlappungsfrei,
2. gleiche Abschlusszeiten teilen eine gemeinsame Grenze,
3. Ereignisse außerhalb des Horizonts bleiben ausgewiesen,
4. die Reihenfolge der Rezeptorfolgen verändert die Partition nicht,
5. ungültige Horizonte werden abgewiesen,
6. der öffentliche Vertrag enthält keinen Feldzustand und keine Halteregel.

## Realer Lauf

Wie in den Audits 002 und 003 wurden drei vorab deklarierte
Ein-Sekunden-Fenster mit Kameraeingang `0` und Audioeingang `1` verwendet.

| Messung | Ergebnis |
|---|---:|
| Beobachtungshorizont | 3.000.000.000 ns |
| lückenlos abgedeckt | 3.000.000.000 ns |
| Zeitspannen insgesamt | 325 |
| ereignistragende Zeitspannen | 324 |
| ereignisfreie Zeitspannen | 1 |
| auditive Ereignisse im Horizont | 309 |
| visuelle Ereignisse im Horizont | 15 |
| Ereignisse vor oder am Start | 0 |
| erst nach dem Horizont abgeschlossen | 2 |
| minimale Zeitspanne | 0,6851 ms |
| mediane Zeitspanne | 2,0478 ms |
| maximale Zeitspanne | 29,3437 ms |

Es wurde kein MCM-Feldschritt ausgeführt. Rohdaten wurden nicht im Ergebnis
gehalten.

## Befund

Eine lückenlose reale Zeitpartition ist technisch möglich. Sie löst die
Ratenverzerrung aber nicht von selbst.

Die meisten Grenzen stammen weiterhin vom schnelleren auditiven Rezeptor. Die
Partition trägt korrekte Dauer zwischen Ereignissen, doch ein vollständiger
Feldvorschlag je Zeitspanne wäre weiterhin nahezu ein Vorschlag je
Sensorabschluss.

```text
lückenlose reale Zeit
!= begründete Feldschrittfolge
```

Die Partition ist deshalb nur eine neutrale Zeitdarstellung.

## Neu sichtbare Grenze

Für eine weitere Entscheidung fehlt die zeitliche Bedeutung eines
Rezeptorzustands auf der Organismusuhr:

- Ist ein reduzierter Zustand nur ein punktuelles Abschlussereignis?
- Trägt er Kontakt über sein gemessenes Aufnahmeintervall?
- Darf er bis zum nächsten Zustand desselben Rezeptors wirken?

Die dritte Variante wäre eine Halteregel. Die erste kann reale Kontaktdauer
verlieren. Die zweite benötigt eine belastbare Abbildung des
rezeptoreigenen Aufnahmefensters auf die Organismusuhr.

Der aktuelle Vertrag misst nur die Dauer des technischen Reads. Er belegt noch
nicht die zeitliche Wirkdauer des darin beschriebenen Weltkontakts.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Als nächstes muss für jeden bestehenden Rezeptortyp geprüft werden, welche
zeitliche Stütze sein reduzierter Zustand tatsächlich besitzt. Erst danach
kann entschieden werden, ob asynchrone Kontakte als Intervalle, Ereignisse
oder eine andere kausal begründete Form in das gemeinsame Feld eintreten.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
