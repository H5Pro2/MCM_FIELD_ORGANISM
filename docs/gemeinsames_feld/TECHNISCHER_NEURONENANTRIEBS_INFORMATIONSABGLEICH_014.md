# Technischer Neuronenantriebs-Informationsabgleich 014

## Status

Passive Strukturprüfung vor `GF_001`.

Der Abgleich prüft ausschließlich, welche Informationen ein bestehender
`MCMNeuronDrive` bereits getrennt trägt. Es wird keine Transition ausgewertet,
kein Kontakt gehalten und kein Feldschritt ausgeführt.

## Vorhandene Rollen

Ein lokaler Neuronenantrieb enthält:

- den vollständig abgeschlossenen vorherigen `MCMNeuron`,
- dessen vorherige `MCMFieldPerception`,
- die aktuelle `MCMFieldPerception`,
- optional die gemessene Zeitspanne des Feldvorschlags.

Dadurch sind bereits getrennt zugänglich:

```text
vorheriger Rezeptorendpunkt
aktueller Rezeptorendpunkt
vorherige Aktivierung
vorheriger Nachhall
verstrichene Vorschlagszeit
```

Wenn vorheriger und aktueller Kontakt vorhanden sind, kann ihre reine
Endpunktdifferenz beobachtet werden, ohne einen neuen Rezeptorpuffer
einzuführen.

## Achseninterventionen

Drei kontrollierte Paare verändern jeweils nur eine Eingangsachse:

| Intervention | veränderte öffentliche Rollen |
|---|---|
| aktueller Kontakt `0,2 -> 0,8` | aktueller Kontakt, Endpunktdifferenz |
| vorheriger Kontakt `0,2 -> 0,6` | vorheriger Kontakt, Endpunktdifferenz |
| Zeitspanne `0,1 s -> 0,5 s` | nur verstrichene Zeit |

Vorherige Aktivierung und vorheriger Nachhall bleiben bei den
Kontaktinterventionen kontrolliert identisch. Rezeptorkontakt ist damit nicht
nur indirekt aus dem schnellen Feldzustand rekonstruierbar, sondern bleibt in
der vorherigen Wahrnehmung eigenständig erhalten.

Fehlt der aktuelle Kontakt, bleibt auch die Endpunktdifferenz ausdrücklich
unbestimmt. Es wird kein Nullkontakt eingesetzt.

## Pfadkollision

Zwei unterschiedliche Kontaktgeschichten besitzen dieselben Endpunkte und
dieselbe gemessene Zeit:

```text
kontinuierlich: 1 -> 1 -> 1
unterbrochen:   1 -> 0 -> 1
```

Ihre Stichproben-Kontaktsummen unterscheiden sich (`3` gegen `2`). Der
bestehende Neuronenantrieb ist dennoch exakt identisch, weil er nur vorherigen
Endpunkt, aktuellen Endpunkt und Gesamtzeit kennt.

```text
gleiche Endpunkte + gleiche Zeit
!= belegte Kontaktkontinuität
```

## Befund

Die vorhandene Struktur ist ausreichend für:

- aktuellen lokalen Rezeptorkontakt,
- vorherigen lokalen Rezeptorendpunkt,
- Endpunktveränderung zwischen zwei vorhandenen Kontakten,
- getrennte vorherige Aktivierung und Nachhalllage,
- verstrichene Zeit eines atomaren Feldvorschlags.

Sie ist nicht ausreichend für:

- unbeobachtete Zwischenkontakte,
- ununterbrochene Kontaktdauer,
- Kontaktmenge innerhalb der Zeitspanne,
- Veränderung bei fehlendem aktuellem Kontakt.

`step_time` ist eine Vorschlagsdauer und keine Rezeptorkontaktdauer.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Ein zusätzlicher vorheriger Snapshotpuffer ist nicht begründet: Der vorherige
Rezeptorendpunkt ist bereits vorhanden. Ebenso wenig ist eine
Änderungsgleichung freigegeben.

Die verbleibende Lücke liegt nicht in fehlenden Endpunkten, sondern zwischen
ihnen. Vor einer Transition muss geprüft werden, wie häufig derselbe Dockpfad
in der realen asynchronen Übergabefolge überhaupt zwei aufeinanderfolgende
verfügbare Kontakte besitzt und wann andere Modalitäten dazwischenliegen.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
