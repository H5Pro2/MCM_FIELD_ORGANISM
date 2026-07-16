# Methodik 020: Passive visuelle Raum-Zeit-Eingangsprüfung

## 1. Forschungsfrage

Welche zeitlich-räumliche Information liegt an den visuellen MCM-Neuronen
bereits kausal vor, wenn eine lokale Lichtfläche zwischen Rasterzellen
wechselt, ohne dass Bewegung oder Richtung programmiert wird?

Geprüft wird nur der Eingang einer möglichen späteren lokalen Feldfunktion:

```text
aktueller eigener Rezeptorkontakt
+ eigener Feldzustand aus dem vorherigen Takt
+ unmittelbare Nachbarlagen aus dem vorherigen Takt
```

## 2. Kontrollierte Bildfolgen

Die Prüfung verwendet kleine synthetische Frames mit genau einer aktiven
Rasterzelle und einem technischen Quellkanal.

Pflichtfolgen:

1. schrittweise Verschiebung über unmittelbar benachbarte Zellen,
2. räumlich gespiegelte Verschiebung,
3. stationäre Wiederholung derselben Zelle,
4. Sprung über mehrere Zellen,
5. Verschiebung mit einem vollständigen Nulltakt dazwischen,
6. Ortswechsel bei gleichzeitigem Wechsel des Quellkanals.

Diese Folgen sind technische Sonden. Sie stellen weder Objekte noch natürliches
Sehen dar.

## 3. Passiver Beobachter

Für jedes Neuron und jeden Takt werden getrennt ausgegeben:

- Neuronenidentität und dreidimensionale Position,
- aktueller eigener Rezeptorkontakt,
- eigene Aktivierung und eigener Nachhall des vorherigen Takts,
- Aktivierungs- und Nachhallunterschied zu jeder vorhandenen Nachbarlage.

Die relativen Nachbarpositionen bleiben erhalten. Der Beobachter bildet daraus
keine Bewegungs-, Richtungs-, Geschwindigkeits- oder Ereignisvariable.

## 4. Unveränderte Feldmechanik

Die visuelle Schnittstelle verwendet während der gesamten Prüfung weiterhin
die `receptor_projection_baseline`:

```text
Aktivierung = aktueller Rezeptorkontakt
Nachhall    = 0
```

Lokale Feldproben werden beobachtet, aber nicht in den nächsten Zustand
eingerechnet. Ein positives Beobachtungsergebnis kann daher nur zeigen, welche
Information für eine spätere lokale Funktion verfügbar wäre.

## 5. Rohdaten- und Bedeutungsgrenze

Die Frames existieren nur während der Rezeptorreduktion. Das Ergebnis enthält
keine Bilder oder Pixel und keine Rollen für Bewegung, Richtung, Objekt,
Person, Szene, Aufmerksamkeit, Bedeutung, Pattern-ID oder Memory.

## 6. Erfolgskriterien

1. Eine benachbarte Verschiebung erzeugt am neuen Ziel aktuellen Kontakt und
   eine aktive passende Nachbarlage aus dem vorherigen Takt.
2. Die gespiegelte Folge spiegelt nur den relativen Nachbaroffset.
3. Stationärer Kontakt trägt eigene Voraktivierung statt aktiver Vor-Nachbarlage.
4. Ein nichtlokaler Sprung erzeugt am Ziel keine aktive unmittelbare Vor-Nachbarlage.
5. Ein Nulltakt unterbricht die unmittelbare lokale zeitliche Verbindung.
6. Ein Kanalwechsel wird nicht als räumliche Nachbaraktivität desselben Kanals
   ausgegeben.
7. Kein Nachhall und keine neue Feldwirkung entstehen.

## 7. Evidenzgrenze

Maximal E2 für das kausale Vorliegen lokaler visueller Raum-Zeit-Eingänge.

Nicht gezeigt sind Wahrnehmung von Bewegung, eine geeignete lokale
Neuronfunktion, zeitliche Reichweite über einen Takt, Beziehung, Lernen oder
visuelle Feldintelligenz.
