# Befund 021: Endlicher realer Kameraadapter

## Kurzurteil

Die explizit adressierte Kameraquelle trägt den endlichen realen Pfad bis zur
visuellen Rezeptorgrenze:

```text
Kameraadapter
-> drei ausdrücklich deklarierte Startframes
-> fünf endliche Aufnahmeframes
-> fünf visuelle Rezeptorzustände
-> 288 lokale Träger je Zustand
```

Ein Audioeingang war an diesem Versuch nicht beteiligt.

## Technischer Lauf

Die Kamera meldete:

```text
Breite:    1920
Höhe:      1080
Bildrate:  ungefähr 30 FPS
```

Die Startphase verbrauchte exakt drei Frames. Davon war ein Frame exakt null
und zwei Frames aktiv. Der Nullframe blieb als technischer Startbefund sichtbar
und erreichte die Rezeptoraufnahme nicht.

Anschließend entstanden aus fünf gelesenen Frames genau fünf aktive
Rezeptorzustände. Jeder Zustand besaß die vorbereiteten `12 × 8 × 3 = 288`
lokalen technischen Träger. Es wurde kein Rohbild gespeichert.

## Getragener Befund

- Die Kameraquelle lässt sich als explizites Gerät öffnen und wieder freigeben.
- 1920-x-1080-Frames erfüllen den vorhandenen Framevertrag.
- Die Startphase ist von Wahrnehmungsframes kausal getrennt.
- Reale Frames erreichen verlustfrei die feste lokale Rezeptorreduktion.
- Start- und Aufnahmezähler bleiben getrennt.
- Zusammenfassungen enthalten keine Rohbilder oder semantischen Rollen.

## Nicht gezeigt

- visuelle MCM-Felddynamik,
- Bewegung oder Richtung,
- Formen, Objekte, Personen oder Szenen,
- natürliche Musterbildung,
- reale audio-visuelle Feldkonstellation,
- Resonanz, Semantik oder innere Bezeichnung.

## Evidenz

```text
expliziter realer Kamerazugriff: E1
reale Kamera bis Rezeptorgrenze: E2
visuelles MCM-Feld:              E0
multimodale reale Konstellation: E0
```

## Bester nächster Schritt

Der nächste Lauf verbindet einen endlichen realen Rezeptorzustand über die
bereits geprüfte 1:1-Dockkarte mit dem visuellen MCM-Feld. Dabei bleibt die
`receptor_projection_baseline` aktiv; eine visuelle Felddynamik wird weiterhin
nicht aus dem Kamerabild abgeleitet.
