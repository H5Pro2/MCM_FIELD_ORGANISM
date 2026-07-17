# Methodik 034: Ringanatomie im simulierten Welt-MCM-Pfad

## 1. Status

Vorregistrierter passiver Integrationsvergleich.

Die in Befund 036 geprüfte `PeriodicSamplingAxis` wird erstmals ausdrücklich
in einem simulierten Sensor-MCM-Feld aktiviert. Es entsteht keine
Feld-zu-Effektor-Verbindung und keine neue Neuronenfunktion.

## 2. Forschungsfrage

Kann der simulierte Ringrezeptor seine bekannte lokale Weltgeometrie im
vollständigen MCM-Pfad bewahren, sodass:

```text
dieselben Welt- und Rezeptorfolgen
→ offene und periodische MCM-Variante
→ gleicher schneller Feldzustand unter receptor_projection_baseline
→ verschiedene lokale Wahrnehmung nur an den zwei Rändern
```

Der Versuch prüft technische Ringtreue. Er prüft keine Wirkung der
zusätzlichen lokalen Proben.

## 3. Wichtige Digestgrenze

Die beiden Feldvarianten müssen verschiedene Geometrieidentitäten tragen:

```text
open:     simulated.field.line7.v1
periodic: simulated.field.ring7.v1
```

Deshalb dürfen vollständige Feldfenster- und Verteilerdigests nicht als
gleich erwartet werden. Die `geometry_id` ist Teil dieser Digests.

Verglichen werden stattdessen getrennt:

```text
identisch:
  dock_id
  modality_id
  field_id
  snapshot_id
  clock_id
  window_start_tick
  window_end_tick
  carrier_ids
  activation
  afterimage

absichtlich verschieden:
  geometry_id
```

Zusätzlich wird ein klar benannter normalisierter Zustandsdigest gebildet, der
ausschließlich `geometry_id` auslässt. Nur dieser Digest muss kollidieren.

Die Geometrie darf nicht aus dem realen Runtime-Zustand entfernt oder
nachträglich überschrieben werden.

## 4. Rückwärtskompatible offene Kontrolle O0

Der bestehende Methodik-031-Pfad bleibt unverändert:

```text
field_geometry = simulated.field.line7.v1
periodic_axes  = ()
```

Sein kanonischer Digest muss weiterhin lauten:

```text
48e7b056b16f6c1dce1efe0def8e26ea732202f525d05952affda10dc80626ff
```

Die vorhandene Funktion `run_simulated_world_mcm_path_probe` wird nicht
umgedeutet. Sie bleibt die historische offene Baseline.

## 5. Periodischer Kandidat P0

Der periodische Kandidat unterscheidet sich anatomisch nur durch:

```text
field_geometry = simulated.field.ring7.v1
periodic_axes  = (
  PeriodicSamplingAxis(axis_index=0, origin=0, size=7),
)
```

Unverändert bleiben:

- sieben Positionen `(0,) ... (6,)`,
- sieben Rezeptor-Neuronen-Docks,
- Offsets `(-1,), (+1,)`,
- Feld-, Layer- und Dockidentitäten,
- Rezeptorwerte,
- gemeinsame Feldzeit,
- `receptor_projection_baseline`,
- neutraler MCM-Verteiler.

## 6. Warum zwei Schritte nötig sind

Ein frisch erzeugtes Feld besitzt vor dem ersten Rezeptorkontakt nur:

```text
activation = siebenmal 0.0
afterimage = siebenmal 0.0
```

Die lokalen Proben des ersten Schritts lesen deshalb nur diesen initialen
Nullzustand. Um die Ringadressierung an einer tatsächlich getragenen Feldlage
zu prüfen, werden zwei kausal getrennte Schritte verwendet:

```text
t0: frisches Feld
t1: erste Weltwirkung und erster Rezeptorkontakt
t2: technische Haltewirkung delta=0 und zweiter Rezeptorkontakt
```

Die Wahrnehmung an `t2` liest die abgeschlossene Ein-Hot-Feldlage aus `t1`.

## 7. Vollständige erste Weltwirkung

Der erste Schritt verwendet erneut:

```text
7 Startpositionen
x 3 delta-Werte
x 2 Ursachen
= 42 Zweige
= 21 Ursachenpaare
```

Für jeden Zweig gilt:

```text
W(t0)
→ Intervention delta mit external oder effector
→ W(t1)
→ Rezeptor R(t1)
→ offenes MCM-Feld F_open(t1)
→ periodisches MCM-Feld F_ring(t1)
```

Beide Feldvarianten erhalten exakt denselben abgeschlossenen
`ReceptorContactFrame`.

## 8. Zweiter technischer Halteschritt

Aus demselben `W(t1)` folgt:

```text
delta = 0
gleiche äußere Ursachenrolle wie im ersten Zweig
→ W(t2) an derselben Position
→ Rezeptor R(t2)
```

`R(t2)` wird erneut identisch an beide Feldvarianten übergeben.

Der Halteschritt ist keine autonome Entscheidung. Er wird vollständig durch
den Testtreiber ausgelöst und erzeugt keinen neuen Effektortyp.

## 9. Erwartete Wahrnehmung an t1

An `t1` müssen offene und periodische Wahrnehmung bereits strukturell genau
zwei Randproben unterscheiden:

```text
Ziel 0 erhält periodisch zusätzlich Quelle 6 bei offset -1
Ziel 6 erhält periodisch zusätzlich Quelle 0 bei offset +1
```

Da beide Quellen noch aus dem initialen Feld `t0` stammen, tragen diese
zusätzlichen Proben:

```text
activation = 0.0
afterimage = 0.0
source_tick = 0
```

Weitere Wahrnehmungsunterschiede sind unzulässig.

## 10. Erwartete Wahrnehmung an t2

An `t2` müssen dieselben zwei Wrap-Proben die abgeschlossene Feldlage aus `t1`
tragen:

```text
Ziel 0, offset -1 liest Quelle 6 aus t1
Ziel 6, offset +1 liest Quelle 0 aus t1
```

Damit gilt abhängig von der Position der Ein-Hot-Anregung:

```text
W(t1) an Position 6
→ Wrap-Probe 6 nach Ziel 0 trägt activation 1.0

W(t1) an Position 0
→ Wrap-Probe 0 nach Ziel 6 trägt activation 1.0

W(t1) an Position 1..5
→ beide zusätzlichen Wrap-Proben tragen activation 0.0
```

Alle Wrap-Proben tragen weiterhin `afterimage = 0.0`.

## 11. Vollständige Branchzählung der getragenen Wrap-Wirklichkeit

In der 42-Zweig-Matrix erreicht jede der sieben Zielpositionen:

```text
3 Kombinationen aus Startposition und delta
x 2 Ursachen
= 6 Zweige
```

Deshalb werden an `t2` erwartet:

```text
6 Zweige mit aktiver Quelle 6 in der Wrap-Probe zu Ziel 0
6 Zweige mit aktiver Quelle 0 in der Wrap-Probe zu Ziel 6
30 Zweige mit zwei zusätzlichen, aber inaktiven Wrap-Proben
```

Diese Zählung wird vor dem Lauf fixiert und exakt geprüft.

## 12. Schneller Zustandsvergleich

Unter `receptor_projection_baseline` muss für beide Schritte und alle Zweige
gelten:

```text
F_open.activation = F_ring.activation = aktueller Rezeptorwert
F_open.afterimage  = F_ring.afterimage  = siebenmal 0.0
```

Die zusätzliche lokale Wahrnehmung darf weder Aktivierung noch Nachhall
verändern.

## 13. Feldfenstervergleich

Für jedes offene und periodische Feldfenster werden zwei Vergleiche geführt:

### Vollständiger Digest

```text
open_digest != periodic_digest
```

Der Unterschied ist wegen `geometry_id` erwartet und notwendig.

### Normalisierter Zustandsdigest

Nach Ausschluss ausschließlich der `geometry_id` gilt:

```text
normalized_open_digest = normalized_periodic_digest
```

Jede weitere Rollendifferenz lässt den Versuch scheitern.

## 14. Verteilervergleich

Beide Varianten werden getrennt an je einen frischen neutralen
`MCMDistributor` mit passendem Dock angehängt.

Erwartet wird:

```text
vollständige Konstellationsdigests verschieden
normalisierte Zustandsdigests ohne geometry_id gleich
jeweils genau ein Feldzustand
keine multimodale Beziehung
```

Ein gemeinsamer Distributor darf die beiden Varianten nicht gleichzeitig als
zwei reale Sinnesfelder interpretieren. Sie sind kontrafaktische Zweige
desselben Weltkontakts.

## 15. Ursachenablation

Für jedes der 21 Ursachenpaare muss getrennt für `t1` und `t2` gelten:

```text
external gegen effector
→ äußere Provenienz verschieden
→ Weltzustand gleich
→ Rezeptorrahmen gleich
→ offene Feldvariante gleich
→ periodische Feldvariante gleich
→ periodische lokale Wahrnehmung gleich
```

Ursache, `delta`, Effort und Provenienz dürfen nicht Bestandteil des
Achsenvertrags oder einer Feldprobe sein.

## 16. Rotations- und Richtungsprüfung

Die periodische Variante wird erneut über:

```text
7 Rotationen x 2 Ringorientierungen = 14 Transformationen
```

geprüft.

Positionen, Trägeridentitäten, Rezeptorwerte und Achsenvertrag werden
gemeinsam transformiert. Nach kanonischer Rückabbildung müssen die lokalen
Wahrnehmungen an `t1` und `t2` exakt kollidieren.

## 17. Reihenfolge und Observer

Geprüft werden:

- normale und umgekehrte Startpositionsreihenfolge,
- normale und umgekehrte `delta`-Reihenfolge,
- normale und umgekehrte Ursachenreihenfolge,
- normale und umgekehrte Neuronenreihenfolge,
- normale und umgekehrte Offsetreihenfolge,
- kein Observer,
- leerer Observer,
- sammelnder Observer,
- unabhängige Wiederholung.

Alle kanonischen Ergebnisse müssen identisch bleiben.

## 18. Resetkontrolle

Nach vollständigem Neuaufbau beider Feldvarianten gilt wieder:

```text
activation = 0
afterimage = 0
tick = 0
keine lokale Wahrnehmung aus einer früheren Geschichte
```

Die periodische Achse bleibt technische Anatomie, trägt aber keine
Kontaktrestspur.

## 19. Öffentliche Rollen

Der neue Versuch darf außen Branch-, Ursachen- und Geometrievergleiche
ausweisen.

Innerhalb von `PeriodicSamplingAxis`, `MCMFieldSample`, `MCMFieldPerception`
und `MCMFieldWindow` bleiben unzulässig:

- Aktionswert oder Effektorwahl,
- Reward oder Ziel,
- Gewicht oder Kopplung,
- Kontinuität oder Beziehung,
- semantische Rolle oder Bezeichnung,
- Provenienz der äußeren Ursache.

## 20. Entscheidungskriterien

Die Aktivierung der Ringanatomie im simulierten Pfad trägt nur, wenn:

1. der historische offene Digest unverändert bleibt,
2. beide Varianten exakt dieselben Rezeptorrahmen erhalten,
3. nur zwei lokale Randproben hinzukommen,
4. die Wrap-Proben an `t1` den Nullzustand aus `t0` tragen,
5. an `t2` exakt 6 plus 6 aktive Wrap-Zweige auftreten,
6. Aktivierung und Nachhall beider Varianten exakt kollidieren,
7. vollständige Digests nur wegen der Geometrie verschieden sind,
8. normalisierte Zustandsdigests exakt kollidieren,
9. alle 21 Ursachenpaare bei `t1` und `t2` kollidieren,
10. alle 14 Transformationen sowie Observer und Reihenfolge neutral bleiben,
11. kein Welt-, Rezeptor-, Feld- oder Verteilerzustand zurückgeschrieben wird.

## 21. Scheiterkriterien

Der periodische Weltpfad bleibt geschlossen, wenn:

- der offene Referenzdigest driftet,
- ein anderer Zustand als `geometry_id` zwischen den Feldfenstern abweicht,
- mehr oder weniger als zwei Wrap-Proben entstehen,
- eine Wrap-Probe denselben Tick liest,
- die erwartete aktive 6-plus-6-Zählung nicht trägt,
- Periodizität Aktivierung oder Nachhall verändert,
- vollständige Digests fälschlich gleichgesetzt werden,
- Ursache oder `delta` in die innere Wahrnehmung gelangt,
- beide kontrafaktischen Varianten gemeinsam verteilt werden müssen,
- eine neue Variable oder Feldregel nötig wird.

## 22. Erwarteter Befund

Erwartet wird:

```text
periodische Anatomie bewahrt den lokalen Ringkontakt im realen MCM-Pfad
+ schneller Zustand bleibt unter der Rezeptorbaseline unverändert
+ Geometrieunterschied bleibt offen sichtbar
```

Dies wäre ein technischer Integrationsbefund, keine kausale Feldwirkung.

## 23. Evidenzgrenze

Ein erfolgreicher Lauf kann höchstens tragen:

```text
aktive Ringanatomie im simulierten Sensorfeld: E1
zweischrittige lokale Ringwahrnehmung:         E1
Rückwärtskompatibilität des offenen Pfads:     E1
kausale Wirkung der Ringproben:                E0
entwickelte Beziehung oder Topologie:          E0
Eigenwirkung und Handlung:                     E0
Feldintelligenz:                               E0
```

## 24. Nicht freigegeben

- Änderung des historischen offenen Methodik-031-Pfads,
- periodische Anatomie für Audio oder Video,
- Nutzung lokaler Proben in einer Feldgleichung,
- Feldkopplung, Gewicht oder Ausbreitung,
- gespeicherte Beziehung oder Memory,
- Feld-zu-Effektor-Auslösung,
- Reward, Ziel, Auswahl, Semantik oder Reflexion.

## 25. Stärkstes Gegenargument

Auch ein vollständig positiver Lauf zeigt nur, dass eine bekannte
Ringgeometrie über zwei technische Feldschritte korrekt erhalten bleibt.

Da `receptor_projection_baseline` jede lokale Feldprobe ignoriert, bleibt die
Ringwahrnehmung funktional wirkungslos. Der Versuch erzeugt keine organische
Feldentwicklung.

## 26. Bester nächster Schritt

Methodik 034 wird exakt als passiver kontrafaktischer Zwei-Schritt-Vergleich
implementiert.

Erst nach einem positiven Befund wird die technische Weltkreisvorbereitung
beendet und wieder eine nichttautologische fehlende Feldfunktion betrachtet.
Eine Feldregel wird nicht aus der Ringanatomie abgeleitet.
