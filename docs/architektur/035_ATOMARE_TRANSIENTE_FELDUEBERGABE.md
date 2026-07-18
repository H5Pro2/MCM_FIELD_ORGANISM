# Atomare transiente Feldübergabe

## Status

Verbindlicher technischer Übergabevertrag auf `E0 / CONTRACT_ONLY`.

Dieser Vertrag verbindet einen bereits vollständig gebildeten
`TransientNeuronInputSet` optional mit `SharedMCMField.advance()`. Er erzeugt
keinen Eingabesatz, bestimmt keinen Feldrhythmus und liest keine lokale Folge.

## Übergabeweg

```text
abgeschlossene Rezeptordistribution
+ vollständiger transienter Neuroneneingabesatz
+ explizite Neuronentransition
-> ein atomarer Vorschlag der gemeinsamen Neuronenschicht
```

Die bestehende skalare Rezeptordistribution bleibt erhalten. Der transiente
Satz ersetzt sie nicht, sondern stellt der expliziten Transition bei Bedarf
die vollständigen lokalen Abschlüsse derselben Vorschlagsspanne bereit.

## Anatomische Prüfung

Vor dem Feldvorschlag wird für jedes Dock-Neuron geprüft:

- die Neuronenidentität gehört zum gemeinsamen Feld,
- Dock- und Carrieridentität entsprechen der bestehenden Dockanatomie,
- jedes angedockte Neuron besitzt genau einen lokalen Eingabevertrag,
- kein fremdes oder zusätzliches Neuron ist enthalten.

Eine bloß passende Anzahl genügt nicht. Die technische Herkunft muss für jede
lokale Eingabe exakt stimmen.

## Gemeinsame Organismusspanne

Der transiente Eingabesatz und die Rezeptordistribution müssen dieselbe
Organismusuhr sowie denselben Start- und Endpunkt tragen.

```text
Eingabe.clock == Distribution.clock
Eingabe.start == Distribution.start
Eingabe.end   == Distribution.end
```

Die technische Auflösung der Vorschlagsspanne bleibt im `MCMFieldStepTime`
explizit. Aus dieser Prüfung entsteht weder ein natürlicher Feldtakt noch eine
gemeinsame Sensor-Hopgröße.

## Wirkungsgleichheit

Die Feldübergabe fügt keine Mechanik hinzu. Ignoriert eine Transition die
transiente Eingangsrolle, bleiben der resultierende Feldzustand und sein
Snapshot exakt gleich wie beim bisherigen Aufruf ohne diese Rolle.

Der Eingabesatz wird nicht gespeichert in:

- `SharedMCMField`,
- `MCMNeuronLayer`,
- `MCMNeuron`,
- `MCMFieldPerception`,
- `SharedMCMFieldSnapshot`.

## Freigabegrenze

```text
vollständige Feldanatomieprüfung: technisch getragen
gemeinsame Zeitspanne:            technisch getragen
atomare Layerübergabe:            technisch getragen
bisheriger Feldaufruf:            unverändert
eingebaute Leserfunktion:         nicht vorhanden
automatische Feldwirkung:         nicht vorhanden
Live-Rezeptoranschluss:           nicht freigegeben
Organischer Feldrhythmus:         offen
```

Der nächste Schritt ist keine Leserfunktion. Zuerst muss geklärt werden, wie
eine reale Feldvorschlagsspanne entstehen kann, ohne Sensorereignisse zu
Feldtakten zu erklären, Zustände zu halten oder unterschiedlich schnelle
Rezeptorfolgen zu verdichten.
