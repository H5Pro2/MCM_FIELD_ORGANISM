# Methodik 019: Saubere visuelle MCM-Schnittstelle

## 1. Zweck

Die bislang getrennt geprüften Bausteine werden zu einem eindeutigen
Ein-Takt-Vertrag verbunden:

```text
ein Kameraframe
-> lokales visuelles Rezeptorraster
-> reduzierte visuelle Rezeptorlage
-> 1:1-Dockkarte
-> visuelle MCM-Neuronenschicht
-> ein vollständiges visuelles Feldfenster
```

Die Schnittstelle kapselt den Transport, nicht die Bedeutung und nicht die
lokale Feldfunktion.

## 2. Unveränderlicher Schnittstellenzustand

Nach jedem Takt entsteht eine neue Schnittstelleninstanz. Sie trägt nur:

- die technische Rasterkonfiguration,
- die lokale dreidimensionale Feldanatomie,
- stabile technische Feld- und Dockidentitäten,
- den nächsten Frameindex,
- den aktuellen reduzierten MCM-Feldzustand.

Ein Rohframe wird während des Aufrufs gelesen und reduziert, aber weder im
Schnittstellenzustand noch im Ergebnis gehalten.

## 3. Visuelle Feldanatomie

Jede Rasterzelle besitzt drei getrennte technische Quellkanäle. Daher liegt
jedes angedockte Neuron an einer Position:

```text
(Rasterzeile, Rasterspalte, Quellkanal)
```

Die technische lokale Feldwahrnehmung tastet nur denselben Quellkanal der vier
unmittelbaren räumlichen Nachbarpositionen ab. Kanäle werden nicht vermischt.
Die Nachbarlagen stammen immer aus dem abgeschlossenen vorherigen Takt.

Diese Geometrie erlaubt lokale Feldwahrnehmung, definiert aber noch nicht, wie
ein Neuron darauf reagiert.

## 4. Explizite Neuronfunktion

Jeder Aufruf muss eine benannte Neuronenübergangsfunktion erhalten. Die
Schnittstelle besitzt keinen versteckten Standard.

Für die technische Freigabe gilt weiterhin:

```text
receptor_projection_baseline:
Aktivierung = aktueller eigener Rezeptorkontakt
Nachhall    = 0
```

Eine zukünftige lokale Feldfunktion kann nur nach eigener Methodik eingesetzt
werden, ohne den Kamera- oder Rezeptoradapter umzuschreiben.

## 5. Zeitvertrag

Jeder Frame erhält genau einen fortlaufenden Index. Das Feld erhält für
denselben Takt ein explizites positives Intervall auf der gemeinsamen
Organismusuhr. Zeit darf weder zurücklaufen noch wiederholt werden.

Technische Videozeit und Organismuszeit bleiben getrennte Rollen.

## 6. Ausgabevertrag

Die Ausgabe enthält nur:

- Frameindex,
- exakten Rezeptorkontaktstatus,
- vollständiges visuelles MCM-Feldfenster.

Sie enthält keine Bilder, Pixel, Objekte, Personen, Szenen, Klassen,
Bedeutungen, Aufmerksamkeit, Pattern-ID oder Memoryrolle.

## 7. Pflichtkontrollen

1. Ein lokaler Kanalwert erreicht genau sein angedocktes Neuron.
2. Alle anderen Neuronen bleiben bei lokaler Einzelanregung null.
3. Ein Rohframe wird weder verändert noch im Ergebnis gehalten.
4. Frameindex, Feldtakt und Organismuszeit schreiten lückenlos voran.
5. Rücklauf oder Wiederholung der Feldzeit wird abgelehnt.
6. Lokale Feldproben stammen nur aus demselben Kanal des vorherigen Takts.
7. Räumliche Gegenrichtungen sind in der Anatomie symmetrisch.
8. Ohne explizite Neuronfunktion kann kein Takt ausgeführt werden.
9. Die Projektionsbaseline erzeugt keinen Nachhall.
10. Öffentliche Rollen enthalten keine Rohdaten oder Semantik.

## 8. Evidenzgrenze

Maximal E2 für die kontrollierte technische Schnittstelle vom realen Frame bis
zum vollständigen visuellen MCM-Feldfenster.

Nicht gezeigt sind visuelle Felddynamik, Bewegung, räumliche Beziehung,
Wiedererkennen, Objektbildung, multimodale Bedeutung oder Feldintelligenz.
