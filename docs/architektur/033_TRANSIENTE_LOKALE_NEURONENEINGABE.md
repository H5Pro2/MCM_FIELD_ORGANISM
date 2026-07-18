# Transiente lokale Neuroneneingabe

## Status

Verbindlicher Informationsvertrag auf `E0 / CONTRACT_ONLY`.

Dieser Vertrag legt fest, welche Teile eines transienten Dockverlaufs lokal
für ein angebundenes Feldneuron sichtbar sein dürfen. Die anschließende
optionale Anbindung an `MCMNeuronDrive` ist im Vertrag
[Transiente Neuronenantriebsrolle](034_TRANSIENTE_NEURONENANTRIEBSROLLE.md)
getrennt geregelt und erzeugt für sich keine Feldwirkung.

## Lokalitätsgrenze

Jeder Rezeptorträger ist über die bestehende Dockanatomie genau einem Neuron
zugeordnet. Für einen Feldvorschlag erhält jedes solche Neuron deshalb nur den
zeitlichen Verlauf seines eigenen Trägers.

```text
transienter Dockverlauf
-> bestehende Carrier-zu-Neuron-Abbildung
-> ein lokaler transienter Verlauf je Dock-Neuron
```

Ein lokaler Kontakt bewahrt:

- reduzierte Kontaktstärke,
- Snapshot- und Carrierherkunft,
- technische Quelluhr und Quellintervall,
- gemessene Read-Zeit auf der Organismusuhr,
- kausale Abschlussreihenfolge.

Das Neuron erhält keine vollständigen fremden Frames, keine globale
Modalitätsfolge und keinen zusammengefassten Audio-Video-Batch.

## Abwesenheit

Wenn innerhalb einer Vorschlagsspanne kein Zustand für den lokalen Träger
abschließt, ist dessen Kontaktfolge leer.

```text
leere Folge
!= Kontaktwert 0
!= letzter Kontakt
!= blockiertes Feld
```

Die Dockanatomie bleibt vorhanden. Es wird kein Ersatzwert erzeugt.

## Keine Wirkung und keine Speicherung

`TransientNeuronInputSet` und `TransientNeuronDockInput` sind technische
Eingangsobjekte außerhalb des Feldzustands. Sie besitzen keine JSON- oder
Snapshotdarstellung und werden nicht in `MCMFieldPerception` aufgenommen.

Nicht festgelegt sind:

- Auswahl oder Gewichtung einzelner Kontakte,
- zeitliche Integration oder Verdichtung,
- Änderung von Aktivierung oder Nachhall,
- Wirkung lokaler Vorfeldproben auf die Folge,
- Beziehung, Topologie, Bedeutung oder Memory,
- eine gemeinsame Modalitätsbewertung.

## Technischer Stand

`project_transient_docks_to_neuron_inputs()` zerlegt den Dockverlauf
verlustfrei anhand der vorhandenen `ReceptorNeuronDockMap`. Reihenfolge der
Dockdeklaration verändert das Ergebnis nicht. Fehlende oder widersprüchliche
Anatomie wird abgewiesen.

## Freigabegrenze

```text
lokale verlustfreie Projektion: technisch getragen
globale Verlaufsfreigabe:       ausgeschlossen
MCMNeuronDrive-Anbindung:       optional und transient getragen
Transition liest Verlauf:       nicht freigegeben
Speicherung im Neuron:          ausgeschlossen
```

Die lokale Projektion und ihre Antriebsrolle bleiben getrennte Verträge. Damit
kann der Verlauf transportiert werden, ohne den bestehenden skalaren Kontakt
still zu ersetzen oder eine Leserfunktion einzubauen.
