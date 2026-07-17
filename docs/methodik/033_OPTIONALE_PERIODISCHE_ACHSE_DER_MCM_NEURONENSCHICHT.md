# Methodik 033: Optionale periodische Achse der MCM-Neuronenschicht

## 1. Status

Vorregistrierter technischer Runtime-Integrationstest.

Es wird noch keine Feldregel, Beziehung oder Effektorverbindung freigegeben.
Die Änderung darf ausschließlich die lokale Probenadressierung einer
ausdrücklich periodischen Sensorachse betreffen.

## 2. Getragener Ausgangspunkt

Befund 035 zeigt auf Ebene einer isolierten Referenz:

```text
offene Linie mit sieben Positionen
+ explizite periodische Randart
-> genau zwei zusätzliche symmetrische Randproben
-> keine Änderung von Aktivierung oder Nachhall unter B1/B2
```

Offen ist, ob dieselbe Anatomie als optionale technische Eigenschaft in die
vorhandene `MCMNeuronLayer` integriert werden kann, ohne offene Felder oder
andere Modalitäten zu verändern.

## 3. Forschungsfrage

Kann die bestehende Neuronenschicht eine explizit deklarierte periodische
Achse bei der lokalen Probenbildung berücksichtigen, während:

- jede bisherige Schicht standardmäßig offen bleibt,
- Befund 035 exakt reproduziert wird,
- technische Kausalität und Atomarität unverändert bleiben,
- keine gespeicherte Kante oder Feldwirkung entsteht?

## 4. Kleinste vorgesehene Zustandsrolle

Die einzige neue technische Rolle ist ein unveränderlicher Achsenvertrag:

```text
PeriodicSamplingAxis
  axis_index : nicht-negativer Dimensionsindex
  origin     : kleinste technische Koordinate der Achse
  size       : endliche Achsengröße
```

Die `MCMNeuronLayer` erhält optional:

```text
periodic_axes: tuple[PeriodicSamplingAxis, ...] = ()
```

Dabei gilt bindend:

```text
periodic_axes = () -> vollständig bisheriges offenes Verhalten
```

Es wird kein allgemeiner `topology`-Zustand, kein Graph und keine
Nachbarstruktur eingeführt.

## 5. Warum nur periodische Ausnahmen gespeichert werden

Offene Ränder bleiben die bestehende Grundannahme. Der Vertrag speichert nur
explizite Ausnahmen für Sensorachsen, deren technische Weltgeometrie bereits
periodisch dokumentiert ist.

Damit wird nicht für jede Schicht eine neue Randklassifikation erzwungen und
keine vorhandene auditive oder visuelle Anatomie still umgedeutet.

## 6. Technische Adressierung

Für eine deklarierte Achse `a` gilt nur beim Erzeugen einer Feldprobe:

```text
wrapped[a] = origin + ((target[a] + offset[a] - origin) modulo size)
```

Für nicht deklarierte Achsen gilt weiterhin:

```text
source[a] = target[a] + offset[a]
```

Existiert die daraus gebildete vollständige Quellposition nicht, fehlt die
Probe wie bisher.

Die Abbildung wird in jedem Schritt neu aus der abgeschlossenen vollständigen
Schichtlage erzeugt. Das Neuron erhält keine Achseninformation und speichert
keinen Randpartner.

## 7. Gültigkeitsbedingungen

Ein periodischer Achsenvertrag ist nur gültig, wenn:

1. `axis_index` innerhalb der Positionsdimension liegt.
2. Jeder Dimensionsindex höchstens einmal vorkommt.
3. `origin` ganzzahlig ist.
4. `size` ganzzahlig und mindestens zwei ist.
5. Alle Neuronenkoordinaten dieser Achse im Intervall
   `origin .. origin + size - 1` liegen.
6. Jede Koordinate dieses Intervalls in der Schicht vorkommt.
7. Die Abbildung verschiedener Proben-Offsets eines Zielneurons nicht auf
   dieselbe Quellposition fällt.
8. Die vorhandene Offset-Symmetrie unverändert erfüllt bleibt.

Eine ungültige Anatomie muss beim Aufbau der Schicht abgelehnt werden, nicht
erst während eines Feldschritts.

## 8. Referenzkandidat

Der einzige positive Integrationskandidat dieses Versuchs lautet:

```text
Positionen       = (0,) ... (6,)
sample_offsets   = (-1,), (+1,)
periodic_axes    = ((axis_index=0, origin=0, size=7),)
geometry_id      = simulated.field.ring7.v1
```

Die bestehende offene Referenz bleibt:

```text
Positionen       = (0,) ... (6,)
sample_offsets   = (-1,), (+1,)
periodic_axes    = ()
geometry_id      = simulated.field.line7.v1
```

Die unterschiedliche Geometrieidentität weist die technische Anatomie offen
aus. Sie ist keine Bedeutung und keine entwickelte Feldrolle.

## 9. Rückwärtskompatibilitätsfamilie O0

Vor jeder positiven Ringprüfung werden alle vorhandenen Schichten ohne
`periodic_axes` ausgeführt.

Verbindlich gilt:

```text
alter Konstruktor ohne neue Angabe
= explizit leere periodic_axes
= bisherige offene Probenadressierung
```

Geprüft werden mindestens:

- bestehende eindimensionale Neuronenschicht,
- auditive Sensor-MCM-Felder,
- visuelle Sensor-MCM-Felder,
- Methodik-031-Weltpfad mit `simulated.field.line7.v1`,
- vollständige bisherige Testsuite.

Der kanonische Digest von Befund 035 muss unverändert bleiben:

```text
1c717cd79cb0a571cfe4e32439c8ba2484b0672da6555765855a5ef811ebbdc5
```

Eine Digeständerung wäre zunächst eine Regression, kein Fortschritt.

## 10. Positive Ringfamilie P0

Die periodische Runtime-Schicht wird aus derselben eingefrorenen Signaturlage
wie Methodik 032 aufgebaut.

Ihre abgeschlossenen `MCMFieldPerception`-Zustände müssen exakt mit der
isolierten Referenz `periodic_reference_perceptions` kollidieren.

Erwartet werden ausschließlich:

```text
Ziel 0, offset -1, Quelle 6
Ziel 6, offset +1, Quelle 0
```

Die Positionen 1 bis 5 müssen mit der offenen Runtime exakt übereinstimmen.

## 11. Keine doppelte Wahrheit

Die isolierte Referenz aus Methodik 032 bleibt nur Testoracle. Die Runtime darf
nicht parallel eine zweite periodische Probenstruktur speichern.

Nach erfolgreicher Integration gilt:

```text
MCMNeuronLayer erzeugt die Runtime-Wahrnehmung
periodic_reference_perceptions prüft sie nur im Test
```

Die Referenz wird nicht in `SensorMCMField`, Distributor oder Organismuszustand
übernommen.

## 12. Atomare Zeit- und Zustandsprüfung

Auch mit periodischer Achse müssen alle Neuronen ausschließlich denselben
abgeschlossenen Zustand `t` lesen.

Geprüft wird:

```text
Schicht(t)
-> offene oder periodisch adressierte Proben aus Schicht(t)
-> alle Vorschläge für t+1
-> atomare vollständige Schicht(t+1)
```

Kein Wrap-Neuron darf einen bereits aktualisierten Zustand desselben Schritts
sehen. Scheitert ein Vorschlag, bleibt die gesamte vorherige Schicht
unverändert.

## 13. Anatomieerhalt beim Fortschreiben

Ein gültiger Feldschritt muss den Achsenvertrag unverändert in die neue
Schicht übernehmen.

Weder Übergang noch Observer dürfen ändern:

- `axis_index`,
- `origin`,
- `size`,
- Geometrieidentität,
- Positionen,
- Proben-Offsets.

Ein Wechsel zwischen `open` und `periodic` während einer laufenden
Schichtgeschichte ist nicht zulässig.

## 14. Baseline-Ablationen

### B1: `hold_state_baseline`

Offene und periodische Runtime müssen aus identischem schnellen Zustand
erzeugen:

```text
identische Aktivierung
identischen Nachhall
unterschiedliche Wahrnehmung nur an den zwei Rändern
```

### B2: `receptor_projection_baseline`

Bei identischem Rezeptorkontakt gilt:

```text
Aktivierung = Rezeptorkontakt
Nachhall    = 0.0
```

Die periodischen Proben dürfen diese Ausgabe nicht verändern.

## 15. Weltpfad- und Ursachenprüfung

Alle 42 Welt-Rezeptor-MCM-Zweige aus Methodik 032 werden erneut verwendet.

Für jedes der 21 Ursachenpaare müssen offene und periodische Runtime getrennt
jeweils kollidieren:

```text
external gegen effector
-> Provenienz außen verschieden
-> Runtime-Feldwahrnehmung innen gleich
```

Die Achsenrolle darf Ursache, `delta`, Effort und Provenienz nicht lesen.

## 16. Symmetrieprüfungen

Die positive Runtime muss dieselben 14 starren Transformationen wie die
isolierte Referenz tragen:

```text
7 Rotationen x 2 Ringorientierungen
```

Nach kanonischer Rückabbildung müssen alle Wahrnehmungen exakt kollidieren.
Technische Iterationsreihenfolge und Reihenfolge der Achsenverträge dürfen das
Ergebnis nicht verändern.

## 17. Negativfamilien

Mindestens abgelehnt werden:

```text
N0: axis_index außerhalb der Positionsdimension
N1: doppelter Vertrag für dieselbe Achse
N2: size kleiner als zwei
N3: boolescher oder nicht-ganzzahliger Achsenwert
N4: Neuronenposition außerhalb des Achsenintervalls
N5: fehlende Koordinate innerhalb der periodischen Achse
N6: Offset-Alias auf dieselbe Quelle
N7: Geometriewechsel innerhalb einer Schichtgeschichte
N8: Übergang entfernt oder verändert periodic_axes
N9: Observer versucht Anatomie zu verändern
```

Jeder Fehler muss vor einem partiellen neuen Schichtzustand abbrechen.

## 18. Observer-, Reihenfolge- und Resetkontrolle

Geprüft werden:

- kein Observer,
- leerer Observer,
- sammelnder Observer,
- normale und umgekehrte Neuronenreihenfolge,
- normale und umgekehrte Offsetreihenfolge,
- bei mehreren Dimensionen vertauschte Reihenfolge unabhängiger
  Achsenverträge,
- vollständiger Neuaufbau der Schicht.

Alle kanonischen Ergebnisse müssen identisch sein. Ein Neuaufbau enthält nur
den offen deklarierten Achsenvertrag, keine Restspur früherer Randkontakte.

## 19. Öffentliche Rollenprüfung

Der neue Achsenvertrag darf ausschließlich enthalten:

```text
axis_index
origin
size
```

Unzulässig sind insbesondere:

- Aktivität oder Nachhall,
- Gewicht oder Kopplung,
- Nutzung oder Kontinuität,
- Ursache oder Wirkung,
- Rolle, Bedeutung oder Semantik,
- Reward, Ziel oder Effektorwert.

## 20. Entscheidungskriterien

Die optionale Runtime-Anatomie trägt nur, wenn gleichzeitig:

1. alle bisherigen offenen Schichten unverändert bleiben,
2. Befund 035 digestgleich reproduziert wird,
3. die periodische Runtime exakt mit der isolierten Referenz kollidiert,
4. genau zwei Wrap-Proben hinzukommen,
5. B1 und B2 den schnellen Zustand unverändert lassen,
6. alle 42 Weltzweige und 21 Ursachenpaare tragen,
7. alle 14 Transformationen äquivariant bleiben,
8. alle Negativfamilien vor atomarer Fortschreibung abbrechen,
9. Observer, Reihenfolge und Neuaufbau neutral bleiben,
10. keine Beziehung, Feldregel oder Effektorrolle entsteht.

## 21. Scheiterkriterien

Die Integration wird verworfen, wenn:

- irgendeine bisherige offene Wahrnehmung verändert wird,
- Periodizität ohne expliziten Achsenvertrag auftritt,
- die Runtime mehr als die zwei erwarteten Wrap-Proben erzeugt,
- ein Alias still zusammengefasst oder doppelt gezählt wird,
- der Achsenvertrag während `advance` verloren geht,
- Aktivierung oder Nachhall allein durch Periodizität verändert werden,
- eine Ursache oder Aktionsrichtung in die Anatomie gelangt,
- für die Integration eine Feldkopplung oder neue schnelle Variable nötig ist.

## 22. Evidenzgrenze

Ein erfolgreicher Lauf kann höchstens tragen:

```text
optionale periodische Runtime-Adressierung: E1
Rückwärtskompatibilität offener Felder:     E1
Ringtreue des simulierten Sensorfeldes:     E1
kausale Wirkung periodischer Proben:        E0
entwickelte Beziehung oder Topologie:       E0
Eigenwirkung und Handlung:                  E0
Feldintelligenz:                            E0
```

## 23. Nicht freigegeben

- Aktivierung der periodischen Achse im produktiven Weltpfad,
- Periodizität für Audio oder Video,
- Feldkopplung oder Ausbreitung,
- gespeicherte Beziehungen oder Memory,
- Verbindung mit `delta` oder einem Effektor,
- Reward, Ziel, Auswahl, Semantik oder Reflexion.

## 24. Stärkstes Gegenargument

Auch eine fehlerfreie Runtime-Integration programmiert nur die bekannte
Ringgeometrie der Simulationswelt. Sie erzeugt keine organische Topologie.

Ihr wissenschaftlicher Wert liegt ausschließlich darin, einen künstlichen
Darstellungsrand aus dem sensorischen Weltkontakt zu entfernen, bevor eine
spätere fehlende Feldfunktion geprüft wird.

## 25. Bester nächster Schritt

Methodik 033 wird exakt gegen die bestehende Schicht implementiert.

Der simulierte Weltpfad bleibt während dieses Versuchs weiterhin offen. Erst
nach einem positiven Integrationsbefund darf separat geprüft werden, ob er die
optionale Ringanatomie ausdrücklich aktiviert.
