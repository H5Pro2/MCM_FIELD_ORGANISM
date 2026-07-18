# Methodik 031: Simulierter Weltrezeptor-zu-MCM-Feldpfad

## 1. Status

Vorregistrierter passiver Integrationstest. Die Intervention bleibt extern und
die vorhandene `receptor_projection_baseline` bleibt der einzige
Neuronenübergang.

## 2. Forschungsfrage

Erreicht die abgeschlossene Rezeptorfolge der simulierten Welt ein eigenes
MCM-Feldfenster und den neutralen Verteiler vollständig, ohne dass `delta`,
Interventionsursache oder technischer Aufwand in den sensorischen Pfad lecken?

## 3. Wichtige Geometriegrenze

Die simulierte Welt besitzt eine zyklische Ringtopologie. Die vorhandene
`MCMNeuronLayer` bildet lokale Wahrnehmung dagegen über gewöhnliche relative
Positions-Offsets und verbindet Feldränder ausdrücklich nicht zyklisch.

Der Versuch prüft deshalb nur:

```text
stabile Trägeridentität
+ exakter Kontaktwert
+ exakte Zeitlage
→ verlustfreier technischer MCM-Feldtransport
```

Er prüft nicht:

```text
Weltposition 6 ist im MCM-Feld lokal mit Weltposition 0 verbunden
```

Die sieben MCM-Neuronen werden für diesen Transport als technische Linie
positioniert. Eine zyklische MCM-Nachbarschaft wird weder ergänzt noch
behauptet.

## 4. Adaptervertrag

Der Adapter akzeptiert ausschließlich einen abgeschlossenen
`SimulatedWorldReceptorFrame`.

Er erzeugt einen vorhandenen `ReceptorContactFrame` mit festen Rollen:

```text
modality_id       = simulated.contact
geometry_id       = simulated.ring7.receptor.v1
snapshot_id       = simulated.receptor.tick.<source_tick>
clock_id          = simulated.world
window_start_tick = source_tick
window_end_tick   = source_tick + 1
carrier_ids       = contact.p0 ... contact.p6
values            = unveränderter one-hot Kontaktvektor
```

Der Adapter liest nur:

- `source_tick`,
- `contact_values`.

Er besitzt keinen Zugriff auf:

- `WorldIntervention`,
- `InterventionCause`,
- `delta`,
- Effort,
- vorherigen Weltzustand,
- Provenienzdigest.

## 5. Technische MCM-Feldanatomie

Für jeden unabhängigen Zweig wird ein frisches Feld erzeugt:

```text
dock_id          = simulated
layer_id         = simulated.layer
field_id         = simulated.field
field_geometry   = simulated.field.line7.v1
positions        = (0,) ... (6,)
sample_offsets   = (-1,), (+1,)
```

Die Dockkarte ordnet jeden Rezeptorträger genau einem MCM-Neuron zu:

```text
contact.p0 → simulated.field.n0
...
contact.p6 → simulated.field.n6
```

Es gibt keine Gewichte, Mehrfachkopie, Zusammenfassung oder internen
Zusatzträger.

## 6. Gemeinsame Feldzeit

Der explizite MCM-Feldzeitraum lautet:

```text
clock_id          = organism.simulated
window_start_tick = receptor.source_tick
window_end_tick   = receptor.source_tick + 1
```

Die technische Weltuhr `simulated.world` bleibt damit von der gemeinsamen
Feldzeit `organism.simulated` unterscheidbar. Beide Intervalle tragen in diesem
Minimalversuch dieselben numerischen Grenzen, aber verschiedene Rollen.

## 7. Neuronenübergang

Es wird ausschließlich verwendet:

```text
receptor_projection_baseline
```

Erwartet wird:

```text
field_window.activation = receptor.values
field_window.afterimage  = siebenmal 0.0
```

Lokale Feldproben werden technisch erzeugt, beeinflussen die Ausgabe dieser
Baseline aber nicht.

## 8. Verteilerpfad

Das abgeschlossene simulierte Feld wird über seinen vorhandenen `MCMDock` an
einen frischen neutralen `MCMDistributor` angehängt.

Die resultierende Konstellation enthält genau:

```text
eine Modalität
ein Feldfenster
sieben Feldträger
```

Sie erzeugt keine multimodale Beziehung und keine gemeinsame Feldwirkung.

## 9. Vollständige Ursachenmatrix

Aus Methodik 030 werden erneut alle Ursachenpaare verwendet:

```text
7 Startpositionen
x 3 delta-Werte
= 21 Ursachenpaare
= 42 Zweige
```

Jeder Zweig beginnt unabhängig bei `tick = 0` und mit einem frischen
MCM-Feld.

Für jedes Paar gilt:

```text
gleiche Startposition
+ gleiches delta
+ external gegen effector
→ gleiche Weltfolge
→ gleicher SimulatedWorldReceptorFrame
→ gleicher ReceptorContactFrame
→ gleiches MCMFieldWindow
→ gleiche verteilte Konstellation
```

Nur die außerhalb dieses Pfades gehaltenen Provenienzdigests dürfen
verschieden bleiben.

## 10. Wrap-Gegenprüfung

Die beiden Weltübergänge

```text
0 + (-1) → 6
6 + (+1) → 0
```

müssen jeweils den korrekten one-hot Kontakt und die korrekte Feldaktivierung
am Zielträger erzeugen.

Der Befund darf nicht als lokale MCM-Nachbarschaft zwischen Träger 6 und 0
interpretiert werden.

## 11. Verlustfreiheitsmessungen

Für jeden der 42 Zweige werden getrennt geprüft:

1. Simulationsrezeptor gegen `ReceptorContactFrame.values`.
2. `ReceptorContactFrame.values` gegen `MCMFieldWindow.activation`.
3. Nullvektor gegen `MCMFieldWindow.afterimage`.
4. Feldfensterdigest gegen verteilten Zustandsdigest.
5. Rezeptorträgerzahl gegen MCM-Trägerzahl.
6. Adapterrollen gegen verbotene Ursachenrollen.

Alle Vergleiche verwenden exakte Gleichheit.

## 12. Observer- und Reihenfolgekontrolle

Ein optionaler Observer darf nur das abgeschlossene passive Zweigergebnis
lesen. Er schreibt nicht in Welt, Rezeptor, Feld oder Verteiler zurück.

Startpositionen, `delta` und Ursachen werden zusätzlich in umgekehrter
Auswertungsreihenfolge geprüft. Das kanonische Gesamtergebnis muss identisch
bleiben.

## 13. Resetgrenze

Der Weltreset erzeugt weiterhin keinen Rezeptorrahmen und deshalb auch kein
MCM-Feldfenster.

Erst eine nachfolgende reguläre Weltaufnahme darf den Resetweltzustand über den
Adapter in das MCM-Feld bringen.

## 14. Entscheidung

Der Pfad trägt nur, wenn:

- alle 42 Zweige verlustfrei sind,
- alle 21 Ursachenpaare ab dem Simulationsrezeptor kollidieren,
- beide Wrap-Fälle am korrekten Träger ankommen,
- kein Ursachenfeld in Adapter, Rezeptorrahmen, MCM-Feld oder Konstellation
  vorhanden ist,
- Observer und Auswertungsreihenfolge neutral bleiben.

## 15. Stärkstes Gegenargument

Der erwartete Befund folgt vollständig aus einer 1:1-Dockkarte und der
vorhandenen Rezeptorprojektionsbaseline. Er zeigt keine MCM-Feldwirkung.

Zusätzlich verliert die lineare MCM-Anatomie die lokale Nachbarschaft des
zyklischen Weltübergangs `6 ↔ 0`. Der Signalwert bleibt erhalten, die
Weltgeometrie aber nicht vollständig.

## 16. Nicht freigegeben

- zyklische MCM-Nachbarschaft,
- Wirkung lokaler Feldproben,
- Verbindung von Feldaktivierung mit `delta`,
- autonome Auslösung oder Handlung,
- Reward, Ziel oder Auswahl,
- adaptive Kopplung oder Beziehungsmemory,
- Rezeptorrückschreibung.

## 17. Evidenzgrenze

Maximal E1 für den technischen Welt-Rezeptor-MCM-Verteiler-Pfad.

E0 bleiben:

- topologietreue Ringwahrnehmung im MCM-Feld,
- kausale MCM-Felddynamik,
- Eigenwirkung,
- Handlung,
- Feldorganisation und Feldintelligenz.

## 18. Bester nächster Schritt

Methodik 031 wird exakt als passiver Integrationslauf implementiert.

Danach muss vor jeder Feld-zu-Effektor-Verbindung entschieden werden, ob die
fehlende zyklische Nachbarschaft eine notwendige technische Sensoranatomie ist
oder ob ihre feste Vorgabe bereits zu viel Weltstruktur in das MCM-Feld
übertragen würde.
