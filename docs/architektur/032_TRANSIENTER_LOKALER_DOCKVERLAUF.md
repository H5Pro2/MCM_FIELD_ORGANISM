# Transienter lokaler Dockverlauf

## Status

Verbindlicher technischer Eingangsvertrag auf `E0 / CONTRACT_ONLY`.

Dieser Vertrag ergänzt keine Feldwirkung. Er schließt nur die Lücke zwischen
einer verlustfrei übergebenen asynchronen Dockfolge und dem atomaren
Feldvorschlag.

## Eingangsgrenze

Eine Feldvorschlagsspanne darf für jeden angeschlossenen Dock alle innerhalb
der Spanne abgeschlossenen reduzierten Rezeptorzustände tragen.

Bewahrt bleiben:

- stabile Dockidentität,
- Modalitätsherkunft und Rezeptorgeometrie,
- vollständiger reduzierter Zustand,
- gemessener Read- und Abschlusszeitraum,
- docklokale Reihenfolge,
- ungeordnete Gleichzeitigkeit gleicher Abschlusszeiten,
- Abwesenheit eines Docks ohne eingesetzten Ersatzwert.

Mehrere Zustände desselben Docks werden weder ausgewählt noch gemittelt. Sie
bleiben ein transienter lokaler Verlauf.

## Transient bedeutet

Der Verlauf existiert ausschließlich als Eingabe eines begrenzten
Feldvorschlags. Er ist nicht Bestandteil von:

- `MCMNeuron`,
- `MCMFieldPerception`,
- `SharedMCMField`,
- Feldsnapshot oder Wiederherstellungszustand,
- organischem Memory,
- Debug- oder Forschungsarchiv.

Der Vertrag besitzt deshalb keine JSON-Persistenz und keine kanonische
Speicherform. Reproduzierbarkeit stammt aus der kontrollierten Eingangsfolge,
nicht aus einem versteckten Verlaufsarchiv im Organismus.

## Keine Leserfunktion

Der Verlauf legt nicht fest:

- welcher Zustand stärker oder wichtiger ist,
- ob Endpunkt, Mittelwert, Integral oder Reihenfolge wirken,
- wie lange ein Kontakt wirkt,
- wie Aktivierung oder Nachhall verändert werden,
- ob eine Folge verdichtet oder wiedererkannt wird,
- wie Topologie, Beziehung oder Bedeutung entsteht.

Er erweitert auch nicht den aktuellen skalaren `receptor_contact`. Die
bestehende Runtime bleibt unverändert.

## Technische Abbildung

```text
ReceptorProposalBatch
-> stabile SharedFieldDocks
-> TransientDockTrajectory
```

`map_proposal_batch_to_transient_docks()` validiert ausschließlich Anatomie
und Verlustfreiheit. Unbekannte Modalitäten, falsche Geometrien, doppelte
Identitäten, widersprüchliche Zähler und Zustände außerhalb der
Vorschlagsspanne werden abgewiesen.

## Freigabegrenze

```text
verlustfreie Dockabbildung:        technisch getragen
Zugriff durch MCMNeuronDrive:      nicht freigegeben
Wirkung auf MCMFieldPerception:    nicht freigegeben
Speicherung im Feldzustand:        ausgeschlossen
Verdichtung oder Memory:           nicht freigegeben
```

Vor einer Anbindung an den Neuronenantrieb muss geklärt werden, welche reine
Informationsrolle der transiente Verlauf dort besitzt. Eine spätere Transition
darf nicht allein durch das Vorhandensein dieser Folge zu einer festen
Zeitleser- oder Verdichtungsmechanik werden.

Die lokale Informationsgrenze ist inzwischen im Vertrag
[Transiente lokale Neuroneneingabe](033_TRANSIENTE_LOKALE_NEURONENEINGABE.md)
umgesetzt. Sie projiziert jeden Trägerverlauf ausschließlich auf sein
angebundenes Neuron und endet weiterhin vor `MCMNeuronDrive`.
